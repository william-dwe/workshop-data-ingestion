import sys, os, secrets, nbformat
from nbclient import NotebookClient
os.environ["FORCE_FALLBACK"] = sys.argv[1]
nb = nbformat.read("workshop_api_webhook.ipynb", 4)
topic = "ws-omptest-" + secrets.token_hex(4)
for c in nb.cells:
    if c.cell_type != "code": continue
    c.source = c.source.replace('"ws-ecommurz-demo"', f'"{topic}"').replace("STREAM_SECONDS = 30", "STREAM_SECONDS = 5")
print("topic", topic)
NotebookClient(nb, timeout=120, kernel_name="python3").execute()
for i, c in enumerate(nb.cells):
    if c.cell_type == "code":
        for o in c.outputs:
            t = o.get("text") or o.get("data", {}).get("text/plain", "")
            if i > 20 or "WARN" in t: print(f"[{i}]", t.strip()[:300])
print("NOTEBOOK OK")
