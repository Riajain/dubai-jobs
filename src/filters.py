from src.sources import Job


class Filter:
    def __init__(self, config: dict):
        self.title_match = [s.lower() for s in config.get("title_match", [])]
        self.title_exclude = [s.lower() for s in config.get("title_exclude", [])]
        self.location_match = [s.lower() for s in config.get("location_match", [])]

    def matches(self, job: Job) -> bool:
        title = (job.title or "").lower()
        if not any(s in title for s in self.title_match):
            return False
        if any(s in title for s in self.title_exclude):
            return False
        location = (job.location or "").lower()
        if not any(s in location for s in self.location_match):
            return False
        return True
