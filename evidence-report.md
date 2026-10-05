# Evidence, including the failure

The first model is not fit for live fraud intervention. The replacement is delivered for shadow scoring only.

## Original experiment, preserved

Duplicate claim IDs were removed before splits. 6,853 decided unique claims through December 2025 trained two CatBoost candidates; January-April 2026 (2,871 claims, 31 frauds) selected depth 5 by average precision. A partner-age ablation did not improve average precision over that candidate. Refitting through April used 9,724 claims. Features included structured submission fields and strictly earlier serial history; outcomes, inspector notes, IDs, source-system labels and free-text instructions were excluded.

The later May-June check had 1,422 decided claims and 36 frauds. ROC-AUC 0.614; AP 0.035; accuracy at 0.5 was 97.19%, below an always-genuine rule's 97.47%. The economic queue reviewed 13 genuine claims and caught zero frauds: Rs 8,320 loss. This is the decisive failure, despite the board's requested accuracy number being above 97%.

## Replacement and honest status

After inspecting the failure and later outcomes, I narrowed learning to the new policy regime. This makes the replacement evaluation exploratory, not a pristine holdout. I used 709 May decided claims (14 frauds) to estimate smoothed partner/amount-band rates and replayed 713 June claims (22 frauds). Shrinkage strengths are fixed at three; the near-cutoff band is Rs 1,950 to below Rs 2,000. No hidden labels were available or used. Final predictions refit on 1,422 May-June decided claims (36 frauds).

June replay: ROC-AUC 0.9348; AP 0.6051 against a 0.0309 prevalence baseline. Conditional case-bootstrap 95% intervals: ROC-AUC 0.861-0.984; AP 0.405-0.773. These intervals do not cover redesign bias, label delays, future partner changes or temporal drift. They are not a promise of hidden performance.

At score >= 0.5: 688 true negatives, 3 false positives, 15 false negatives, 7 true positives. Accuracy 97.48%, error 2.52%. The capacity/economic queue is a different decision rule: 14 reviews, 9 frauds caught, 5 genuine repairs delayed; review precision 64.29%, fraud recall 40.91%. It missed 13/22 frauds (59.09%) and 5/14 reviews (35.71%) were genuine. Fraud from partners not already implicated in May, and an expensive inspected claim, are important failure cases. A change in partner behavior or a new attacker can bypass the score.

Money: Rs 13,436 detected fraudulent claims minus 5 * Rs 380 goodwill minus 14 * Rs 260 contact = Rs 7,896. At 750 claims/month versus 713 observed: Rs 8,306/month. This assumes every detected fraud payout is stopped, review costs one contact, and excluded undecided claims resemble decided claims. At 50% prevention the replay saving drops to Rs 1,178. No reviewer salary or hosting cost is supplied. Break-even prevention is 5,540/13,436 = 41.2%. These are scenario estimates, not realized savings.

## Prospective evidence to collect

Next week: run shadow scoring; preserve normal customer processing. Verify May investigation outcomes were available at the time of replay. Timestamp each outcome and record who was investigated, including a random audit sample from low-score claims. Review lead owns the 40/month limit. Do not consume all 40 reviews simply because they exist. A later pilot can allocate a small random audit component within that limit; forecasted savings above do not include that different allocation.

Report weekly: decided claims and pending claims by cohort, fraud precision/recall, reviews, genuine delays, loss prevented, contact costs, partner and amount-band drift. Promote only after positive prospective net value and acceptable repair delay are demonstrated. Freeze/refit artifact snapshots with a version; do not update labels silently.

## Service checks

`test_service.py` verifies schema and invalid records, batch/API parity, explanations, unknown references, body limits, a missing-model response and UI availability. `evidence/service_checks.json` gives the executed results and local warm-model latency. UI walkthrough additionally exercises an actual browser request. No paid calls, API keys or external model service are used.
