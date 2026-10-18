import json, nbformat, pandas as pd
src = open("helpers.py").read()

# notebook helpers cell must mirror helpers.py exactly
nb = nbformat.read("workshop_api_webhook.ipynb", 4)
assert any(c.cell_type == "code" and c.source == src for c in nb.cells), "helpers cell != helpers.py"
assert all(not c.get("outputs") for c in nb.cells if c.cell_type == "code"), "notebook has outputs"

import helpers as h
ev = lambda i, m: {"id": i, "event": "message", "message": m}
good = lambda oid, pid=1, q=1: json.dumps({"order_id": oid, "customer": "x", "product_id": pid, "qty": q, "ts": "t"})

# malformed skipped and counted (bad json, missing key, wrong type, non-object)
bad = ["not json", "{}", json.dumps({"order_id": "z", "customer": "c", "product_id": "1", "qty": 1}), "[1]", "5"]
df, skipped, before = h.clean_orders([ev(str(i), m) for i, m in enumerate([good("a")] + bad)])
assert skipped == len(bad) and len(df) == 1 and before == 1

# duplicate order_id removed
df, skipped, before = h.clean_orders([ev("1", good("a")), ev("2", good("a")), ev("3", good("b"))])
assert (before, len(df), skipped) == (3, 2, 0) and list(df.order_id) == ["a", "b"]

# revenue math
prods = pd.DataFrame({"id": [1, 2], "title": ["A", "B"], "category": ["c", "c"], "price": [10.5, 4.0]})
orders, _, _ = h.clean_orders([ev("1", good("a", 1, 2)), ev("2", good("b", 2, 3)), ev("3", good("c", 2, 1))])
en = h.enrich(orders, prods)
assert list(en.revenue) == [21.0, 12.0, 4.0]
top = h.top_products(en)
assert list(top.title) == ["A", "B"] and list(top.revenue) == [21.0, 16.0]

# cursor logic returns only new ids
evs = [ev(str(i), good(str(i))) for i in range(5)]
assert [e["id"] for e in h.new_since(evs, "2")] == ["3", "4"]
assert h.new_since(evs, "4") == []
assert len(h.new_since(evs, None)) == 5

# fallback sample data: 2 duplicates + 1 malformed
df, skipped, before = h.clean_orders(h.SAMPLE_EVENTS)
assert (skipped, before - len(df)) == (1, 2) and len(h.SAMPLE_ORDERS) == 15
# smee: no link means nothing is sent and nothing crashes; a forced outage returns no channel
assert h.send_webhook(None, {"order_id": "x"}) is None
h.FORCE_FALLBACK = True
assert h.new_smee_channel() is None
h.FORCE_FALLBACK = False
print("all tests passed")
