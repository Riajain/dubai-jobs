from datetime import datetime, timezone

import requests

from src.sources import Job

TIMEOUT = 15


def fetch(company: dict) -> list[Job]:
    token = company["token"]
    name = company["name"]
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    r = requests.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    jobs = []
    for j in data:
        ts = j.get("createdAt")
        posted = (
            datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat()
            if isinstance(ts, (int, float)) else ""
        )
        location = (j.get("categories") or {}).get("location", "")
        jobs.append(Job(
            id=f"lever:{token}:{j['id']}",
            title=j.get("text", ""),
            company=name,
            location=location,
            url=j.get("hostedUrl", ""),
            posted_at=posted,
            source="lever",
        ))
    return jobs
