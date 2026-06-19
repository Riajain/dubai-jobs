#!/usr/bin/env python3
"""Detect which ATS a careers page uses and print a companies.yml entry.

Usage: python scripts/discover_ats.py <careers_url> [--name "Company Name"]
"""
import argparse
import re
import sys

import requests

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "\
     "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"

PATTERNS = [
    ("greenhouse", re.compile(r"(?:boards\.greenhouse\.io|boards-api\.greenhouse\.io/v1/boards)/([a-zA-Z0-9_-]+)")),
    ("greenhouse", re.compile(r"job-boards\.greenhouse\.io/([a-zA-Z0-9_-]+)")),
    ("lever",      re.compile(r"jobs\.lever\.co/([a-zA-Z0-9_-]+)")),
    ("ashby",      re.compile(r"jobs\.ashbyhq\.com/([a-zA-Z0-9_-]+)")),
    ("workday",    re.compile(r"(https?://[a-z0-9-]+\.(?:wd\d+\.)?myworkdayjobs\.com/[^\s\"'<>]+)")),
]


def fetch(url: str) -> str:
    r = requests.get(url, headers={"User-Agent": UA}, timeout=20, allow_redirects=True)
    r.raise_for_status()
    return r.text


def detect(html: str) -> tuple[str, str] | None:
    for ats, pat in PATTERNS:
        m = pat.search(html)
        if m:
            return ats, m.group(1)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--name", default=None)
    args = ap.parse_args()

    try:
        html = fetch(args.url)
    except Exception as e:
        print(f"# ERROR fetching {args.url}: {e}", file=sys.stderr)
        return 2

    result = detect(html)
    name = args.name or args.url
    if not result:
        print(f"# {name}: no known ATS detected at {args.url}")
        print(f"# Try opening the careers page, clicking 'View jobs', then re-run with that URL.")
        return 1

    ats, token = result
    if ats == "workday":
        print(f"  - name: {name}")
        print(f"    ats: workday")
        print(f"    # TODO open {token} in browser, search for any role, copy the")
        print(f"    # cxs endpoint from devtools Network tab (POST to /wday/cxs/.../jobs)")
        print(f"    endpoint: {token.rstrip('/')}/wday/cxs/<tenant>/<site>/jobs")
        print(f"    external_url_base: {token.rstrip('/')}")
        print(f"    search_text: software engineer")
    else:
        print(f"  - name: {name}")
        print(f"    ats: {ats}")
        print(f"    token: {token}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
