import requests

from src.sources import Job

TIMEOUT = 15


def fetch(company: dict) -> list[Job]:
    token = company["token"]
    name = company["name"]
    url = f"https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=false"
    r = requests.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    jobs = []
    for j in data.get("jobs", []):
        jobs.append(Job(
            id=f"ashby:{token}:{j['id']}",
            title=j.get("title", ""),
            company=name,
            location=j.get("location", "") or j.get("locationName", ""),
            url=j.get("jobUrl", "") or j.get("applyUrl", ""),
            posted_at=j.get("publishedAt", "") or "",
            source="ashby",
        ))
    return jobs
