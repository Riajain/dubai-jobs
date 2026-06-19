import logging
import sys
from pathlib import Path

import yaml

from src import filters, notifier, state
from src.sources import Job, greenhouse, lever, ashby, workday, linkedin

ROOT = Path(__file__).resolve().parent.parent
SOURCES = {
    "greenhouse": greenhouse.fetch,
    "lever":      lever.fetch,
    "ashby":      ashby.fetch,
    "workday":    workday.fetch,
}

log = logging.getLogger("jobalert")


def load_yaml(name: str) -> dict:
    return yaml.safe_load((ROOT / name).read_text())


def fetch_all(companies_cfg: dict) -> list[Job]:
    out: list[Job] = []
    for c in companies_cfg.get("companies", []):
        ats = c.get("ats", "").lower()
        if ats not in SOURCES:
            log.info("skip %s (ats=%s not yet configured)", c.get("name"), ats)
            continue
        try:
            jobs = SOURCES[ats](c)
            log.info("%s: %d raw postings", c["name"], len(jobs))
            out.extend(jobs)
        except Exception as e:
            log.warning("%s fetch failed: %s", c.get("name"), e)

    li_cfg = companies_cfg.get("linkedin") or {}
    if li_cfg.get("enabled"):
        try:
            li_jobs = linkedin.fetch(li_cfg)
            log.info("linkedin: %d raw postings", len(li_jobs))
            out.extend(li_jobs)
        except Exception as e:
            log.warning("linkedin fetch failed (expected from GH Actions IPs): %s", e)
    return out


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    config = load_yaml("config.yml")
    companies_cfg = load_yaml("companies.yml")

    seen = state.load()
    flt = filters.Filter(config)

    all_jobs = fetch_all(companies_cfg)
    log.info("fetched %d total postings across all sources", len(all_jobs))

    new_matches: list[Job] = []
    new_ids: list[str] = []
    emitted: set[str] = set()
    for j in all_jobs:
        if j.id in seen or j.id in emitted:
            continue
        if flt.matches(j):
            new_matches.append(j)
            new_ids.append(j.id)
            emitted.add(j.id)

    log.info("%d new matching jobs after filter+dedupe", len(new_matches))

    if new_matches:
        notifier.send_digest(
            jobs=new_matches,
            sender=config["sender"],
            recipient=config["recipient"],
        )
        log.info("email sent to %s", config["recipient"])

    state.save(seen | emitted, new_ids)
    return 0


if __name__ == "__main__":
    sys.exit(main())
