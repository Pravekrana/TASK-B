# Kestrel Home - warranty review assistant

**Delivered mode: shadow only.** Scores are available, but do not hold, reject or delay a customer's repair based on them. An exploratory replay is encouraging; a prospective pilot is still required.

## Start on a clean machine

Use Python 3.12, Windows/macOS/Linux. No API key or paid service is needed.

```sh
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux instead: source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:8000. Endpoint: `POST /predict`; readiness: `GET /health`. The supplied private folder includes the fitted model and references. Missing artifacts produce a useful 503 response; the screen still starts. Bind is localhost only, with no debug mode. No claims are logged intentionally; exception traces may appear locally.

Public source package: run `python demo_setup.py` before `python app.py` to create clearly synthetic artifacts. Demo scores are not assignment predictions. The script refuses to overwrite private model artifacts.

Example request (synthetic claim; partner/product IDs are lookup keys):

```json
{"claim_id":"DEMO-001","submitted_at":"2026-07-15 10:30","partner_id":"SP3033","sku":"KH-AF-01","product_serial":"KH123456789","days_since_purchase":210,"claim_amount_inr":1600,"photo_attached":"Y","partner_inspected":"N","customer_prior_claims":0}
```

The response contains `score` (higher = greater fraud risk), four plain-language reasons, warnings, expected net review value, model version, and shadow-mode guidance. Score is a smoothed frequency, not a fraud verdict or guaranteed calibrated probability. Unknown references are warned about. Text and outcome labels are ignored. Money is INR; input timestamps are local IST without a timezone suffix.

## Reproduce and verify

```sh
python train_model.py    # historical CatBoost experiment; ~7 minutes locally
python train_policy.py   # final policy-era model and predictions; run AFTER baseline
python test_service.py
```

Original downloaded names can keep their prefixes. Training finds `*-train.csv` etc. The baseline command temporarily replaces predictions and metadata; always finish with `train_policy.py`. For a quick final-only refit, artifacts/references from this delivery must remain present. Both commands are seeded. No outcome labels from test are used.

Final model: May/June decided claims only; partner and amount-band fraud frequencies, shrunk by three prior-equivalent observations at each level. Amount bands: below Rs 1,950; Rs 1,950 to below Rs 2,000; Rs 2,000 and above. Age of partner, free text, notes, claim ID and serial are not model inputs. Do not interpret partner associations as causality or blacklist partners.

Optional future pilot queue: select at most 40 positive-value claims per calendar month, ordered by `p*amount - (1-p)*380 - 260`. A single-record API cannot enforce a global monthly quota; use a queue owner. Outcome timestamps and label availability are absent, so historical learning assumes May outcomes were available by June. Verify that assumption before deployment.

## Deliverables and ownership

- `predictions.csv`: 2,252 unique IDs, sample-submission order, scores in [0,1].
- `memo-to-ritu.pdf` and `.md`: decision and money, one page.
- `evidence-report.md`, `data-audit.md`, `evidence/*.json`: evaluation, failures and service checks.
- `submission-form.md`: every question answered, blocked public links explicitly identified.
- `walkthrough.mp4`: local screen walkthrough if recording succeeds; accompanying transcript documents any limitation.
- `public-source.zip`: source and synthetic demo only. Never publish the raw pack, artifacts, row-level evidence, predictions, memo or private recording publicly.

Production work remaining: authentication, encrypted storage, claim queue/quotas, outcome timing, random audit labels, calibration/drift monitoring and a kill switch. No public deployment, CRM integration or automatic denial is implemented. Monday owner should read the memo, check `/health`, and keep shadow mode until a monitored pilot is approved.
