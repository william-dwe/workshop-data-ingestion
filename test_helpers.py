import json, nbformat, pandas as pd
src = open("helpers.py").read()

# notebook helpers cell must mirror helpers.py exactly
nb = nbformat.read("workshop_api_webhook.ipynb", 4)
assert any(c.cell_type == "code" and c.source == src for c in nb.cells), "helpers cell != helpers.py"
assert all(not c.get("outputs") for c in nb.cells if c.cell_type == "code"), "notebook has outputs"

import helpers as h
ev = lambda i, m: {"id": i, "event": "message", "message": m}
good = lambda oid, pid=1, q=1: json.dumps({"order_id": oid, "customer": "x", "product_id": pid, "qty": q, "ts": "t"})

def run_cell(marker, **ns):
    """Run the notebook's own cell (the one containing `marker`) on the given variables."""
    cell = next(c.source for c in nb.cells if c.cell_type == "code" and marker in c.source)
    ns.update(json=json, pd=pd)
    exec(cell, ns)
    return ns

def clean(events):
    ns = run_cell("rows, skipped = [], 0", raw_events=events)   # step 5d
    return ns["orders"], ns["skipped"], len(ns["all_orders"])

# malformed skipped and counted (bad json, missing key, wrong type, non-object)
bad = ["not json", "{}", json.dumps({"order_id": "z", "customer": "c", "product_id": "1", "qty": 1}), "[1]", "5"]
df, skipped, before = clean([ev(str(i), m) for i, m in enumerate([good("a")] + bad)])
assert skipped == len(bad) and len(df) == 1 and before == 1

# duplicate order_id removed
df, skipped, before = clean([ev("1", good("a")), ev("2", good("a")), ev("3", good("b"))])
assert (before, len(df), skipped) == (3, 2, 0) and list(df.order_id) == ["a", "b"]

# revenue math: run the notebook's own 5e cell on a tiny dataset
prods = pd.DataFrame({"id": [1, 2], "title": ["A", "B"], "category": ["c", "c"], "price": [10.5, 4.0]})
orders, _, _ = clean([ev("1", good("a", 1, 2)), ev("2", good("b", 2, 3)), ev("3", good("c", 2, 1))])
ns = run_cell("enriched = orders.merge", orders=orders, products=prods)
assert list(ns["enriched"].revenue) == [21.0, 12.0, 4.0]
assert list(ns["top"].title) == ["A", "B"] and list(ns["top"].revenue) == [21.0, 16.0]

# fallback sample data (ntfy forced down): poll returns the cursor-based slice of SAMPLE_EVENTS
h.FORCE_FALLBACK = True
assert len(h.poll("t")) == 15 and len(h.poll("t", "s12")) == 2 and h.poll("t", "s14") == []
assert h.poll("t", "no-such-id") == h.SAMPLE_EVENTS    # unknown cursor = everything
h.FORCE_FALLBACK = False
# fallback sample data: 2 duplicates + 1 malformed
df, skipped, before = clean(h.SAMPLE_EVENTS)
assert (skipped, before - len(df)) == (1, 2) and len(h.SAMPLE_ORDERS) == 15
# a forced smee outage returns no channel and nothing crashes
h.FORCE_FALLBACK = True
assert h.new_smee_channel() is None
h.FORCE_FALLBACK = False
print("all tests passed")
