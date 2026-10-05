# Ritu: approve shadow scoring, not automatic fraud decisions

**Decision:** Use a small local review assistant in shadow mode next week. Keep customers' existing repair process. Do not launch automatic claim rejection or blame newer partners.

**The number:** 97% accuracy is not a useful success target here. Saying every claim is genuine already gives 97.47% on May-June claims. My first model reached 97.19% but caught none of 36 frauds and would have cost Rs 8,320 in needless delays and contacts. I discarded it.

**What changed:** Fraud moved toward claims below Rs 2,000 after inspection was removed on 1 May. The replacement learns from that period and flags claims using recent partner outcomes and amount bands. In an exploratory June replay of 713 claims, it reviewed 14, caught 9 of 22 frauds and delayed 5 genuine repairs. It still missed 13 frauds. This is encouraging evidence, not an independent live test: I designed the replacement after examining those outcomes.

**The rupees:** Rs 13,436 of identified fraud minus Rs 1,900 goodwill and Rs 3,640 contact cost gives Rs 7,896 net, about Rs 8,306 at 750 claims a month. That assumes every identified fraud is stopped and one contact per review. At 50% prevention, the saving is only Rs 1,178 in that replay. Reviewer labor and hosting are additional costs. No paid model calls are needed.

**Next week:** Name one review lead. Run scores silently, verify investigation dates and record pending cases. Keep the 40-review monthly ceiling, and do not fill it with negative-value cases. Agree a small random audit within that capacity to measure what low scores miss. Track fraud caught, genuine repair delays and net rupees, then decide on a limited pilot using prospective results.

**Safeguards:** A score is a reason to check evidence, never proof of fraud. Verify Shield cover separately. Keep customer and operational data private. The email thread listed in the pack was absent; the policy and README were the available authority.
