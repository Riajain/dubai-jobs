from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    id: str
    title: str
    company: str
    location: str
    url: str
    posted_at: str
    source: str
