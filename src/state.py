import json
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent.parent / "state.json"
MAX_SEEN = 5000


def load() -> set[str]:
    if not STATE_FILE.exists():
        return set()
    data = json.loads(STATE_FILE.read_text())
    return set(data.get("seen_job_ids", []))


def save(seen: set[str], newly_added_order: list[str]) -> None:
    """Persist seen IDs, capped at MAX_SEEN via FIFO eviction of oldest non-new IDs."""
    if len(seen) <= MAX_SEEN:
        ids = list(seen)
    else:
        new_set = set(newly_added_order)
        old_ids = [i for i in seen if i not in new_set]
        keep_old = old_ids[-(MAX_SEEN - len(new_set)):] if len(new_set) < MAX_SEEN else []
        ids = keep_old + newly_added_order
    STATE_FILE.write_text(json.dumps({"seen_job_ids": ids}, indent=2) + "\n")
