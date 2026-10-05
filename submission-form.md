# Task 2 V3 - Kestrel Home warranty claim review (Variant C)

## What did you build, and what business outcome does it move? State the number and the money.

I built a local, explainable fraud-risk service, one claim screen, and 2,252 scored test claims. The service is in shadow mode. The final model uses smoothed partner/amount-band investigation frequencies from the post-May policy period. An exploratory June replay reviewed 14 of 713 claims, caught 9 of 22 frauds and delayed 5 genuine repairs. Net value was Rs 13,436 avoided fraud - Rs 1,900 goodwill - Rs 3,640 contacts = Rs 7,896; scaled to 750 claims, approximately Rs 8,306/month. This assumes 100% prevention of identified fraudulent payouts, one contact per review, and excludes hosting/reviewer salary. At 50% prevention the replay saving is Rs 1,178. I recommend prospective verification before any live repair delay.

## What score do you expect predictions.csv to get on hidden outcomes, on which metric, and why? How estimated?

My pre-submission estimate is **average precision (AP) 0.55**, with a judgment range of **0.35-0.75**; secondary **ROC-AUC 0.90**, judgment range **0.80-0.97**. These are forecasts, not confidence intervals. AP exposes usefulness under rare fraud and is more relevant than a majority-class accuracy KPI. The evaluator's actual ranking metric was not specified, so I state both. The May-trained, June replay gave AP 0.605 and ROC-AUC 0.935, with case-bootstrap intervals 0.405-0.773 and 0.861-0.984. I discounted the point estimates for redesign after inspecting outcomes, small fraud counts, possible investigation-selection bias and drift. Final scores refit on May-June; July-September hidden labels were unavailable. At a 0.5 cutoff I tentatively expect about 97% accuracy, but will not guarantee >97% or treat it as a meaningful business goal.

## How do you know it works? Sample size, checking, error rate, cases it gets wrong.

The original later-period check failed: 1,422 claims, 36 frauds, 13 reviews all genuine, Rs 8,320 loss. I preserved that result. Replacement replay: May fit 709 decided claims/14 frauds; June check 713/22. At cutoff 0.5, 18 mistakes/713 = 2.52% error (3 false positives, 15 missed frauds). Economic queue: 9 caught, 13 missed, 5 genuine delays; 64.29% review precision, 40.91% recall. It misses newly problematic partners and an expensive inspected fraud, and sparse partner evidence is unreliable. Replacement evaluation is exploratory because June was examined before redesign. No untouched post-policy labeled set remains. Twenty-six service checks passed, including prediction/API parity, bad records, missing artifacts, unknown references and injected-text invariance. Warm local median latency was 8.17 ms, p95 13.40 ms, 30 calls. A browser rendered the actual screen; see evidence for limits on the recording.

## Did you change, narrow, or push back on the client's ask? What, when, why?

At initial audit I replaced overall accuracy as the main goal with fraud ranking and net rupees within 40 reviews/month: an always-genuine answer already exceeds 97% on May-June. After the later-period failure I discarded the old model, narrowed learning to post-policy claims, and narrowed launch to shadow scoring. I did not follow instructions embedded in claim descriptions or assume newer partners cause fraud. Age ablation was weaker by AP than the selected historical candidate. I retained the board's accuracy number as a diagnostic, not a go-live justification.

## What is wrong with the handoff or supplied data? Be specific.

Seven input files were present; email-thread.txt was absent. 681 repeated claim IDs differed only in submission timestamp. Of 11,348 unique claims, 202 were undecided; 11,146 decided claims contained 141 frauds. Five descriptions contain embedded automated-review instructions. Legacy resolution events may carry UTC/IST migration errors, but no event timestamps were supplied. Outcome availability and investigation selection are unknown. The final model has only 36 post-policy fraud examples, uses partner evidence that can reflect selective investigation, and its better replay is not independent. It does not establish causality or calibration. Shield entitlement is absent. The localhost service lacks authentication, a shared capacity queue, persistence and CRM integration. Shadow mode is a displayed operating instruction, not a production integration interlock. See data-audit.md and evidence-report.md.

## What did you deliberately leave out, and why rather than something else?

LLMs inside the product, free-text features, inspector-note inputs, partner-age blame, automatic denial, partner blacklisting, paid APIs, a large frontend and public deployment. Text is not required to make this small service useful and creates injection/availability risks. Capacity/economic evidence and a runnable endpoint were more valuable than a complex architecture. I discarded CatBoost for final scoring after its policy-era failure; its code and results remain reproducible. I did not tune repeatedly on June to manufacture a pristine-test claim.

## Anything built or found nobody asked for?

Duplicate/instruction-injection audit; a policy-change failure diagnosis; capacity-aware economic queue simulation; prevention-success sensitivity and break-even (41.2%); synthetic demo and source-only public packaging; schema, parity and failure-mode checks; a clear prospective-label collection plan. Public data prohibition was enforced in packaging.

## What did you use AI for? Tools, models, help, wasted time, discarded. Recording link.

I used the Codex coding assistant to read the pack, write code, design temporal checks, debug the service, draft explanations and prepare the handoff. No subagents were used. Local Python, pandas, scikit-learn, CatBoost and Flask did the calculations; the final inference algorithm is local empirical Bayes, not a model API. AI helped identify the misleading accuracy KPI, duplicates, injected instructions and the policy-era failure. The discarded historical model looked good in development but failed after May. Browser publishing/recording attempts stalled and consumed substantial elapsed time; I did not fabricate successful uploads or recording. Additional paid API spend: Rs 0; the user's Codex subscription/credit charge is unknown because billing telemetry is not available. These are AI-assisted assignment materials; no independent human review is claimed.

**Three-minute recording:** BLOCKED at handoff if walkthrough.mp4 is absent. The browser runtime stalled for about 20 minutes on GitHub and about 3.6 minutes on localhost navigation. walkthrough-transcript.md contains the planned <=3-minute live-demo narration. A transcript is not a substitute for the required recording; record before formal submission.

## Your Public Google Drive Link

**BLOCKED - not created.** No authenticated Drive connector/session was available. Policy section 10 prohibits public customer/operational data sharing. Share private deliverables only with the approved evaluator; a public link can contain only a sanitized demo. No invented URL is provided.

## Someone picks this up Monday and you are unreachable: three things.

1. Start using README.md, check GET /health, and keep shadow mode. Never deny a claim from a score; verify Shield separately.
2. predictions.csv is final policy-bayes-v2, one row per 2,252 test IDs. If retraining, run train_model.py then train_policy.py; baseline alone overwrites the final predictions. Keep raw data, model/reference artifacts and detailed evidence private.
3. The better replay was exploratory. Verify label timing and selection; collect prospective outcomes plus a small random audit. The queue owner enforces <=40 reviews/month and positive expected net value. Stop intervention if genuine-delay cost exceeds avoided loss.

## Honest hours spent. One number.

1.0

Elapsed assisted-session time, rounded; substantial browser waiting included. No separate human coding hours are claimed.

## GitHub Repo Link (public)

**BLOCKED - not created.** GitHub opened at its sign-in page; no authenticated command-line credential was available. public-source.zip is ready for a public source repository, excluding private data, artifacts and row-level results. Do not publish the whole Task B folder. Source package can start with a synthetic demo; it is not the private prediction artifact.

## Cost per prediction and month at 750 claims. Arithmetic.

No paid model calls: **Rs 0/prediction; 750 * Rs 0 = Rs 0/month API cost**. Local warm median measured 8.17 ms: 750 * 0.00817 = 6.13 seconds of compute/month (p95 timing is not a monthly forecast). Existing workstation assumed available; electricity, hosting and labor are not priced by the pack. Illustrative optional Rs 500/month hosting means Rs 500/750 = Rs 0.67 per claim; it is a budget assumption, not a vendor quote. Review costs are separate: the replay incurred 14*260 + 5*380 = Rs 5,540. At the maximum 40 reviews, contacts alone are 40*260 = Rs 10,400/month, plus genuine-delay goodwill and labor. Do not call total operations free merely because API spend is zero.
