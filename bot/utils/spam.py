import time
from collections import defaultdict
from threading import Lock

_lock = Lock()
_actions: dict = defaultdict(list)
THRESHOLD = 5
WINDOW = 60  # seconds


def is_spam(user_id: int, action: str = "default") -> bool:
    key = f"{user_id}:{action}"
    now = time.time()
    with _lock:
        _actions[key] = [t for t in _actions[key] if now - t < WINDOW]
        if len(_actions[key]) >= THRESHOLD:
            return True
        _actions[key].append(now)
    return False
