import requests

from src.sources import Job

TIMEOUT = 20


def fetch(company: dict) -> list[Job]:
    """Workday companies declare the full cxs endpoint in companies.yml under `endpoint`,
    plus an `external_url_base` (e.g. https://company.wd1.myworkdayjobs.com/en-US/External)
    that we join with each posting's externalPath to form the apply URL.

    Optional `search_text` narrows results server-side (e.g. "software engineer")."""
    name = company["name"]
    endpoint = company["endpoint"]
    base = company["external_url_base"].rstrip("/")
    payload = {
        "appliedFacets": {},
        "limit": 50,
        "offset": 0,
        "searchText": company.get("search_text", "software engineer"),
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    r = requests.post(endpoint, json=payload, headers=headers, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    jobs = []
    for p in data.get("jobPostings", []):
        ext = p.get("externalPath", "")
        jobs.append(Job(
            id=f"workday:{name}:{p.get('bulletFields', [''])[0] or ext}",
            title=p.get("title", ""),
            company=name,
            location=p.get("locationsText", ""),
            url=base + ext if ext else "",
            posted_at=p.get("postedOn", ""),
            source="workday",
        ))
    return jobs
