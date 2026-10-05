# Planned live screen walkthrough - about 2 minutes 30 seconds

Recording status: browser access stalled repeatedly. If walkthrough.mp4 is absent, the required screen recording is still outstanding. This narration is provided to make finishing it quick; do not label the transcript as a recording. Use the live app and source/evidence pages, no slides. Do not publicly share private evidence; use synthetic data for a public demonstration.

0:00-0:25 - Open README.md and the localhost screen. "I built a small local claim review assistant. It has no paid API calls. The employee gets a score, readable evidence and a separate warranty/inspection warning. It starts in shadow mode."

0:25-0:50 - Open evidence-report.md. "The board wanted 97% accuracy. Predicting genuine for everyone already passes that target. My original CatBoost model looked useful in January-April but caught none of the later 36 frauds and would have lost Rs 8,320. I discarded it."

0:50-1:15 - Open risk_model.py. "Inspection changed in May. I replaced the model with smoothed post-policy partner and amount-band investigation frequencies. This uses no partner age, text instructions or inspector notes. Sparse evidence is pooled, not interpreted as proof."

1:15-1:45 - On the live screen, score a synthetic claim; change the amount to 1,995 and show the response. "One request returns reasons and net review value. A separate monthly queue must enforce the 40-review capacity. The app never automatically rejects a customer."

1:45-2:10 - Open the evidence report again. "The replacement's exploratory June replay caught 9 of 22 frauds from 14 reviews, delayed 5 genuine repairs, and saved an estimated Rs 7,896 under the stated cost assumptions. It missed 13 frauds. I examined June before redesign, so this is not an independent test."

2:10-2:30 - Open the audit and submission form. "I removed 681 duplicate claim rows, excluded undecided labels and ignored injected instructions. The email thread was missing. Next week I would shadow score, verify outcome timing and collect a random audit. Private data stays out of the public source package."
