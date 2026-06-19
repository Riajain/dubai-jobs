import requests

from src.sources import Job

TIMEOUT = 15


def fetch(company: dict) -> list[Job]:
    token = company["token"]
    name = company["name"]
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    r = requests.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    jobs = []
    for j in data.get("jobs", []):
        jobs.append(Job(
            id=f"greenhouse:{token}:{j['id']}",
            title=j.get("title", ""),
            company=name,
            location=(j.get("location") or {}).get("name", ""),
            url=j.get("absolute_url", ""),
            posted_at=j.get("updated_at", "") or j.get("first_published", ""),
            source="greenhouse",
        ))
    return jobs
