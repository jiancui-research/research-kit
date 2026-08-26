> Loaded by `/research.review` when the venue family is security (CCS, NDSS, Oakland/S&P,
> USENIX Security, RAID, ACSAC). Distilled from the reviewer guidelines these venues publish.

# Reviewing a security paper

**The stance these venues ask for:** look for the reason the work might be promising and say
how to get it there, rather than hunting for a reason to reject. Your review has two audiences -
the authors, who need to know how to improve regardless of the decision, and the committee,
which needs the decision justified. Junior researchers read these; write one you would want.

## What a security reviewer actually probes

These are the axes a strong review covers. A review that skips one has a hole in it.

1. **Problem focus and motivation.** Is the threat real and worth the page count? "Motivation is
   weak" is not reviewable - say whether you doubt the *problem* or the *presentation of it*.
2. **Threat model.** Explicit, labelled, and bounded: adversary goal, knowledge, capability, and
   what they may **not** do. An unbounded adversary makes the evaluation unfalsifiable. A threat
   model that quietly shifts between design and evaluation is a finding.
3. **Technical contribution.** Judge the work presented, not the work you would have preferred.
   Novelty here is broader than a new algorithm: a novel result, novel engineering, a novel
   measurement, or a novel benchmark all count.
4. **Evaluation.** Do the experiments as presented test each claim? Baselines fair and tuned,
   variance reported, no leakage, and the dataset's construction stated well enough to trust.
5. **Related work and comparison.** Does the delta hold as the paper argues it, or does it lean
   on work it never compares against?
6. **Data construction and sharing.** How was ground truth established, by whom, with what
   agreement, and what is released?
7. **Case studies.** Do the illustrative cases support the general claim, or are they the only
   places it holds?
8. **Generalizability.** What breaks outside the measured setting - other platforms, other
   populations, later time periods?
9. **Ethics and disclosure.** Human subjects, scraped or personal data, live systems touched,
   and whether affected parties were told before publication. Several of these venues require
   the section of every paper, systematization included.
10. **Presentation.** Self-contained on one read, without chasing appendices.

## Rules these venues set that change a review

- **Unpublished work cannot diminish novelty.** Preprints and white papers may be raised as
  useful pointers, never as grounds to reject and never as a required comparison.
- **Missing artifacts.** These venues expect code, data, or proofs backing a claimed
  contribution unless the paper explains their absence. Where a contribution cannot be checked
  because the artifact is missing and unexplained, a reviewer may simply **decline to credit
  that contribution** - and should say so plainly rather than treating it as a fatal flaw.
- **Do not deanonymize.** The requirement is that the submission is anonymized per the CFP, not
  that you cannot guess. Do not go looking.
- **Rebuttals are short.** Author responses are capped, often around 700 words. Rank your
  questions so the top ones are answerable in that budget, and do not read a skipped minor
  point as a concession.

## Decision vocabulary

Beyond accept and reject, these venues commonly offer **minor revision** (small changes, the
outcome genuinely uncertain, re-reviewed by the same reviewers in a few weeks) and
**conditional accept with shepherding** (small changes whose outcome is certain, checked by one
shepherd). The distinction matters when you write: if you are asking for a revision, the union
of everything the panel asks for has to be doable in a few weeks.

## Length

Four to five substantial paragraphs covering the axes above is the working floor. A very short
review is usually a bad one - it cannot have given the authors anything to act on.
