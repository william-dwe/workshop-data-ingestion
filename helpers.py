#@title Helpers - just run this cell { display-mode: "form" }
# Nothing to edit here. These small functions are used by later cells.
import json, os, time, uuid
from datetime import datetime, timezone
import requests
import pandas as pd

NTFY = "https://ntfy.sh"
SMEE = "https://smee.io"
# Only for testing: pretend ntfy and smee are down.
FORCE_FALLBACK = os.environ.get("FORCE_FALLBACK") == "1"

# Sample data used when ntfy is down or says "too many requests" (HTTP 429).
# Messages are STRINGS, just like real ntfy messages. Note: 2 duplicates, 1 bad message.
def _o(oid, who, pid, qty):
    return json.dumps({"order_id": oid, "customer": who, "product_id": pid,
                       "qty": qty, "ts": "2026-10-09T10:00:00+00:00"})
SAMPLE_ORDERS = [_o("a1", "Ana", 1, 2), _o("a2", "Budi", 11, 1), _o("a3", "Citra", 12, 3),
    _o("a4", "Dewi", 13, 1), _o("a5", "Eko", 14, 2), _o("a6", "Fajar", 15, 1),
    _o("a7", "Gita", 1, 1), _o("a8", "Hadi", 11, 4), _o("a9", "Indra", 12, 1),
    _o("b1", "Joko", 13, 2), _o("b2", "Kiki", 1, 5), _o("b3", "Lina", 14, 1),
    _o("a2", "Budi", 11, 1),            # duplicate of a2
    _o("b1", "Joko", 13, 2),            # duplicate of b1
    "oops this is not json {"]          # malformed message
SAMPLE_EVENTS = [{"id": f"s{i}", "event": "message", "message": m}
                 for i, m in enumerate(SAMPLE_ORDERS)]

def new_smee_channel():
    """Make a free smee.io receiver URL. Returns the URL, or None if smee is down."""
    try:
        if FORCE_FALLBACK:
            raise requests.ConnectionError("FORCE_FALLBACK is on")
        r = requests.get(f"{SMEE}/new", allow_redirects=False, timeout=10)
        url = r.headers["Location"]
        if not url.startswith(SMEE + "/"):
            raise ValueError("unexpected reply from smee")
        return url
    except Exception as e:
        print(f"WARNING: could not reach smee.io ({e}).")
        return None

def publish(topic, payload):
    """POST a dict as JSON text to ntfy. Returns the message id, or None on failure."""
    try:
        if FORCE_FALLBACK:
            raise requests.ConnectionError("FORCE_FALLBACK is on")
        r = requests.post(f"{NTFY}/{topic}", data=json.dumps(payload), timeout=10)
        r.raise_for_status()
        return r.json()["id"]
    except Exception as e:
        print(f"WARNING: could not publish to ntfy ({e}).")
        return None

def poll(topic, since="all"):
    """Ask ntfy for stored messages after `since`. Falls back to SAMPLE_EVENTS."""
    try:
        if FORCE_FALLBACK:
            raise requests.ConnectionError("FORCE_FALLBACK is on")
        r = requests.get(f"{NTFY}/{topic}/json", params={"poll": 1, "since": since}, timeout=10)
        r.raise_for_status()
        events = [json.loads(line) for line in r.text.splitlines() if line.strip()]
    except Exception as e:
        print(f"WARNING: ntfy not available ({e}). Using SAMPLE_ORDERS instead.")
        ids = [ev["id"] for ev in SAMPLE_EVENTS]
        start = ids.index(since) + 1 if since in ids else 0   # only events AFTER the cursor
        return SAMPLE_EVENTS[start:]
    return [e for e in events if e.get("event") == "message"]  # skip open/keepalive

def stream(topic, seconds, on_event):
    """Listen live for `seconds`, call on_event(event) for each real message."""
    end = time.time() + seconds
    try:
        if FORCE_FALLBACK:
            raise requests.ConnectionError("FORCE_FALLBACK is on")
        with requests.get(f"{NTFY}/{topic}/json", stream=True, timeout=(10, seconds)) as r:
            r.raise_for_status()
            try:
                for line in r.iter_lines():
                    if line and json.loads(line).get("event") == "message":
                        on_event(json.loads(line))
                    if time.time() > end:
                        break
            except requests.RequestException:
                pass  # quiet topic: read timed out, that is the normal end
    except Exception as e:
        print(f"WARNING: could not stream from ntfy ({e}).")
