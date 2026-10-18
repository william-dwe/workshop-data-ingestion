# Data Ingestion with APIs and Webhooks (workshop notebook)

Hands-on Google Colab notebook for **"The Art of Connecting Data: APIs and Webhooks for Non-Engineers"**
(analytic × ecommurz). You only run cells and change one value per exercise. No coding from scratch.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/william-dwe/workshop-data-ingestion/blob/main/workshop_api_webhook.ipynb)

## What you need
- A Google account and a browser. Nothing to install.
- No API keys, no sign-ups. The notebook uses two free public services:
  [DummyJSON](https://dummyjson.com) (a fake shop catalogue, the API half) and
  [ntfy.sh](https://ntfy.sh) (push messages over HTTP, standing in for a webhook sender).

## What you will do
1. Pull data from an API (pagination, rate limits).
2. Receive pushed events, webhook style.
3. Compare pull and push.
4. See where both fit in a data pipeline.
5. Build a mini pipeline for a class "shop": produce, consume (batch and streaming), clean, deduplicate, enrich.

## Notes
- The class topic in Part 5 is **public**. Do not put personal data in orders.
- If ntfy is unreachable or rate-limited, the notebook falls back to sample data and prints a warning.

## For maintainers
- `helpers.py` is mirrored exactly in the notebook's helpers cell. `test_helpers.py` checks this and tests the cleaning logic: `python test_helpers.py` (needs `pandas`, `nbformat`).
- `run_nb.py <0|1>` runs the notebook headless (`1` forces the fallback path). Needs `nbclient`, `ipykernel`.
