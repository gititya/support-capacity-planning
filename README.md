# When AI takes the easy support work

I think the wrong question in the AI-and-support debate is: “How many tickets did the model handle?” The useful question is: “What work is left, how long does it take, and what does the whole system cost?”

LLMs can take a meaningful share of customer contacts. They can also cut the cost of a support operation. I do not think either fact proves that a team should make proportional layoffs.

This does not make support employment safe, or require every team to grow. A company can cut roles, and a system that resolves work cheaply and reliably can lower staffing needs.

My argument is narrower. A count of contacts resolved by AI is not a count of human hours removed. It is not a staffing plan. It is not evidence that the remaining team can be reduced in the same proportion.

Support work is not a neat average. A team gets password resets, delivery disputes, broken integrations, and cases where the first answer did not work. If an LLM takes the simple questions first, the work left for people may take more judgment, investigation, and care.

That is the premise of my [capacity model](https://github.com/gititya/support-capacity-planning): a what-if calculation, not a forecast. It assumes AI resolves easier contacts first, unresolved work returns to people, and the remaining human work takes longer. That premise may be wrong for a given queue. Easy for a person is not automatically easy for a model.

## A scenario that saves money

The model does show a substantial saving under its stated assumptions. Start with 20,000 weekly contacts. Route 65% to AI. Let AI resolve 80% of what it receives. Give simple contacts a five-minute human handle time and hard contacts 35 minutes. Give each person 30 productive hours a week, at $30 an hour. Charge AI $0.75 for each resolved contact.

AI resolves 10,400 contacts in that scenario. People still receive 9,600 contacts: 7,000 contacts never go to AI, and 2,600 routed contacts come back. The model puts the remaining work at 27.8 minutes per contact, because the easier part has been removed. That produces about 148 full-time equivalents of workload before any review of AI output or assistance for the remaining staff. These are workload equivalents, rounded to the nearest whole number, not a roster that accounts for shifts and service targets. A flat 20-minute average would have said 107. That would understate the workload by 41 people in this model.

Now add two minutes of human oversight for each AI resolution. The model rises to 160 people. Then add AI assistance that saves 12% of the handle time on the work people keep. It falls to 142.

Compare that with the same model with no AI: 222 people. At the selected inputs, the AI case has a real modeled cost saving. Human work plus AI fees totals about $135,627 a week, compared with $200,000 for the no-AI case. The 142 figure is not an argument against savings. It is an argument for counting the work and the fees before declaring the savings.

The arithmetic is inspectable. The model counts AI resolutions, residual human hours, oversight, assistance, and AI fees. It does not model arrival patterns, service targets, training, quality failures, rework, wage changes, vendor minimums, or system-management cost. A real workforce plan needs those things.

“AI handled 52% of contacts” and “we can remove 52% of people” are different statements. Here, AI resolves 52% of contacts, while staffing moves from 222 to 142, a 36% reduction. That difference follows from the inputs. Another queue can differ. Measure it.

## Volume, workload, and cost are three different numbers

Support leaders need to keep three measures apart.

**Volume** is contacts arriving. Total customer demand and contacts reaching people are separate counts; automation can reduce the second without reducing the first.

**Workload** is the human time needed for the contacts that remain, plus the time needed to review, correct, and support the AI. It tells me staffing pressure.

**Net cost** is human labor, AI fees, and the other operating costs I choose to include. It tells me whether the intervention pays for itself.

AI can reduce contacts reaching people while their workload falls by a smaller proportion. It can lower workload while net cost rises if the vendor fee or oversight burden is high. It can reduce both human contacts and workload while also lowering net cost. I do not need to pretend those outcomes are the same to make the case for careful capacity planning.

There is useful evidence for both the assistance case and the need for restraint. The NBER study of a staggered rollout to 5,179 customer-support agents found a 14% average rise in issues resolved per hour, with larger gains for novice and lower-skilled workers and little effect for the most experienced group. That is evidence that AI can improve human productivity in one deployment; it is not a universal staffing ratio. [NBER working paper](https://www.nber.org/papers/w31161)

Klarna’s 2025 annual report says its AI assistant handled 80% of customer-service chats during 2025. The filing also estimates $39 million of savings in 2024, based on internal data after the assistant launched. That is a serious company result and a useful case to inspect. It is still the company’s estimate, not independent proof that another support operation will get the same result. [Klarna Form 20-F](https://www.sec.gov/Archives/edgar/data/2003292/000200329226000007/klar-20251231.htm)

The wider picture does not settle the employment question. Gartner reported that 85% of 321 surveyed support leaders were expanding human-agent responsibilities as AI reduced volume and shifted work, while 31% had implemented or planned AI-driven layoffs through the first quarter of 2027. That is a survey of leaders, not an employment census. [Gartner, April 2026](https://www.gartner.com/en/newsroom/press-releases/2026-04-28-gartner-survey-finds-eighty-five-percent-of-service-and-support-leaders-are-expanding-human-agent-responsibilities-despite-expectations-of-mass-ai-layoffs) Gartner also forecasts that more than half of customer-service organizations will double technology spending by 2028 without an equivalent reduction in talent. A forecast is not an observed result. [Gartner, March 2026](https://www.gartner.com/en/newsroom/press-releases/2026-03-31-gartner-predicts-over-50-percent-of-customer-service-organizations-will-double-their-technology-spend-by-2028)

## Growth changes the decision

The clearest value in the model is growth. Raise the same scenario from 20,000 to 28,000 weekly contacts. It returns 199 people with AI and 311 without it. The 112-person gap means fewer hypothetical hires in the no-AI scenario. It does not show that 112 current people were laid off, or that they would have been hired in reality.

That distinction matters. A shrinking business may cut staff. A growing business may avoid hiring at the old rate. Another may keep the team and spend capacity on follow-up or complex cases. The model cannot choose among those decisions.

## Ideas I think hold up

- Measure human workload after automation, not only contacts resolved by AI.
- Put oversight, rework, and AI fees in the same business case as labor savings.
- Treat avoided future hiring and present-day layoffs as different claims.

## Ideas I would argue against

- “AI handled most contacts, so most support roles are no longer needed.”
- “Harder remaining work proves AI cannot reduce costs.”
- “One vendor result, survey, or model scenario tells us what every support team should do.”

The practical next step is simple: take one real queue, classify the work AI resolved, the work it returned, the time people spent on each, and the cost of supervision. Then test the model against that record before using it to make a staffing decision.

## Try the model

Open `index.html` in a browser and change the inputs. It is a what-if model: easier work being resolved first is an assumption to examine, not a universal fact about AI. A nonzero staffing floor depends on the chosen workload and unresolved share; it disappears for zero workload or fully resolved work with no oversight.

The displayed headcount rounds the calculation. Cost uses the unrounded hours, so multiplying rounded headcount by weekly cost can differ slightly. This model does not account for every staffing constraint, service level or shift pattern. It is not an employment forecast or staffing recommendation.
