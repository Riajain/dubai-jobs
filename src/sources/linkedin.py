import random
import time

from src.sources import Job


def fetch(linkedin_config: dict) -> list[Job]:
    """Best-effort LinkedIn scrape via python-jobspy. Raises on failure so caller
    can swallow it — LinkedIn frequently rate-limits GH Actions IPs."""
    from jobspy import scrape_jobs

    queries = linkedin_config.get("queries", [])
    results_per_query = linkedin_config.get("results_per_query", 25)
    hours_old = linkedin_config.get("hours_old", 24)

    jobs: list[Job] = []
    for i, q in enumerate(queries):
        if i > 0:
            time.sleep(random.uniform(3, 8))
        df = scrape_jobs(
            site_name=["linkedin"],
            search_term=q["keywords"],
            location=q["location"],
            results_wanted=results_per_query,
            hours_old=hours_old,
            country_indeed="United Arab Emirates",
        )
        if df is None or df.empty:
            continue
        for _, row in df.iterrows():
            job_id = row.get("id") or row.get("job_url")
            if not job_id:
                continue
            jobs.append(Job(
                id=f"linkedin:{job_id}",
                title=str(row.get("title") or ""),
                company=str(row.get("company") or ""),
                location=str(row.get("location") or ""),
                url=str(row.get("job_url") or ""),
                posted_at=str(row.get("date_posted") or ""),
                source="linkedin",
            ))
    return jobs
