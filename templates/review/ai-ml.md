> Loaded by `/research.review` when the venue family is AI / ML / NLP (ACL and ARR venues,
> NeurIPS, ICML, ICLR, EMNLP). Distilled from the reviewer guidelines these venues publish.

# Reviewing an AI or ML paper

## Read it twice, deliberately

**Skim first, before looking at the results.** Identify the research question and whether the
methodology could answer it, and whether the claims are scoped to what is being tested. Fixing
the question in mind before seeing the numbers is what stops hindsight bias from deciding the
review.

**Then read for soundness.** The paper should stand on its own without the appendix; open the
appendix only when the paper points you there for a specific issue.

## What goes wrong in these papers

**Methodology**
- **A model used as a judge must be validated for the task at hand.** "We had a model rate
  fluency" needs agreement with human judgement *on this task*, not in general.
- Reproducibility means hyperparameters, hardware, and a stated plan for code and data.
- Data quality problems that go undisclosed - contamination between train and test, noisy
  labels - are serious, not cosmetic.
- Model and benchmark choice has to be justified and tied to the claim. "We evaluate on [suite]"
  invites: why that one?
- Proofs complete, correct, and referenced where used.

**Results**
- Claim scope must match what was measured. Performance on a benchmark is evidence about that
  benchmark, not about the underlying capability it is named after.
- Properly tuned baselines, appropriate statistics, no fishing.
- Variance: error bars, confidence intervals, or a significance test. A single run is a data
  point, not a result.
- Hypotheses presented as tested conclusions, not as speculation dressed up.
- Framing that outruns the delta ("solves X" for a modest reduction) is an overclaim finding.

**Artifacts and ethics**
- Human data collection needs approval and disclosed compensation.
- Release terms stated: licence and access conditions for datasets and models.

**General**
- The research question and contribution stated plainly, early.
- Methodology justified by current practice, not by "prior work did it this way".
- Related work represented fairly, and citations that actually say what they are cited for -
  worth checking directly, since generated citations are frequently wrong or invented.
- Key terms defined where they first do work.

## Review form conventions

These venues typically split the review into a **summary** the authors can check for
misreadings, **strengths**, **weaknesses**, and **questions**, then score **soundness** (is the
work correct and supported) separately from **excitement or impact** (does it matter). Keep the
two apart: a sound paper you find unexciting is not a soundness problem, and saying so in the
right box is what lets an area chair weigh it properly.

Recent work matters, but only what was published far enough ahead of the deadline to be
reasonably known - typically a few months. Concurrent preprints are pointers, not obligations.

## On writing the review with a model

Every one of these venues now has a policy, and the common shape is: assistance with phrasing
is fine, and generating the substance is not. Do not paste an unpublished manuscript into a
service that retains it. A review whose argument was produced by a model is the failure mode
the policy exists to prevent - and submissions themselves sometimes carry text aimed at
manipulating an automated reviewer, which is worth flagging to the chairs rather than obeying.
