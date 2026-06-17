# Benchmark paper — section skeleton

Use this skeleton when the paper's core question is "how do we let the field compare apples to apples?". A benchmark paper's proof obligation is four concrete ingredients: a precisely defined **task**, a defensibly constructed **dataset**, operationally defined **metrics**, and a panel of real **baselines**. If any of the four is hand-waved, the paper is rejected regardless of polish.

**Venue framing (pick one and keep it consistent):**
- **Security venues** open *threat-first*: lead with a real-world risk; the benchmark is the means to expose it. Threat model is a standalone section.
- **AI/ML venues** open *gap-first*: lead with a measurement/evaluation gap; articulate desiderata; the benchmark is the end in itself. Adversary/assumptions folded inline.

Replace every bracketed placeholder. Delete sections that do not apply, but never delete the four-ingredient obligations.

---

## Abstract

One paragraph, fixed tuple: **gap → benchmark name → scale → headline number(s) → one-line takeaway**.

- State the gap in one sentence: what no existing benchmark captures.
- Name the benchmark and give its scale concretely: **N items, K task types/categories, M models evaluated**.
- Lead with the headline result, not the method (e.g., "even frontier models reach only B% under [hard condition]").
- Close with the takeaway and a public-artifact footnote (link to data + harness).

## 1. Introduction

Four to five contribution bullets after the opening. Cover, at minimum: the **dataset**, the **evaluation protocol/metrics**, the **baselines evaluated**, and the **findings**.

- **Security style:** open with the concrete threat or failure mode, then state the gap ("no benchmark measures whether systems are vulnerable to X"), then contributions.
- **AI style:** open with the measurement gap in current evaluation, articulate **desiderata** the benchmark must satisfy (realism, robustness, scale, measurability, contamination-resistance), then present the benchmark as a self-contained contribution.
- Scope the novelty claim precisely: "first benchmark for X **in setting Y**", never bare "first benchmark for X" - the qualified noun survives review.
- Link the public artifact here as well as in the abstract.

## 2. Related benchmarks / related work

Position against existing benchmarks, not just topical prior work. For each closest benchmark, state in one line **how yours differs and why a new one was needed** (new task, larger/cleaner data, contamination-resistant, harder, more realistic).

- A compact comparison table (columns: scale, task coverage, ground-truth source, leakage control, this work) is highly persuasive here.
- Place this section early if the contribution is heavily comparative; otherwise it can follow construction.

## 3. Task formulation

Define the task as a tuple in one paragraph: **(input = [...], output = [typed ...], success = [exact criterion])**.

- Be exact about what counts as a **true positive, false positive, partial match, and hallucination**. Vague success criteria are a rejection.
- If the task has multiple subtasks, give the tuple per subtask.
- Show the smallest concrete instance (one worked example) before the full machinery.

## 4. Design / construction

Describe construction as a **pipeline of named quality gates**, each justified. Example gates:

- **Informativeness** - discard items that lack the signal the task is meant to test.
- **Validation / reproducibility** - retain only items whose ground truth was independently reproduced or verified.
- **Deduplication and leakage check** - remove near-duplicates and items overlapping known training corpora.

Also document:
- **Sources** concretely (where items came from, sizes, dates, license/consent basis).
- **Ground-truth process** with inter-annotator agreement or cross-validation evidence; describe annotator instructions and adjudication.
- **A single statistics table** for a one-glance dataset summary (counts per category, length distribution, difficulty splits).
- **Bias and coverage** openly: who/what is over- or under-represented, and why that is acceptable for the claims.

## 5. Validation (is the benchmark sound?)

Show the benchmark measures what it claims and discriminates between systems.

- **Ground-truth quality:** report agreement metrics; show error rate on a manually audited sample.
- **Discriminative power:** show the benchmark separates weak from strong systems (it is neither saturated nor random).
- **Metric validity:** if you use an automatic judge or LLM-as-judge, **validate it against human/ground-truth labels on this task** and report the correlation - an unvalidated judge score means nothing to a reviewer.
- **Contamination / leakage:** dedicate at least one paragraph to how you detect and control test-set memorization.

## 6. Evaluation protocol

Make the scoring exactly reproducible.

- Define each metric with a one-sentence operational definition (plus a formal/mathematical definition at AI venues).
- Specify the **scoring harness, prompt template, decoding settings (temperature, max tokens), and seeds**.
- State how partial credit and ties are handled, and how runs are aggregated (mean over K runs, with variance).

## 7. Evals / leaderboard

Evaluate at least **3-5 representative baselines** spanning a sensible axis (open vs closed, small vs large, general vs domain-specific). Justify the panel.

- Report results in a leaderboard table with **variance (error bars / CIs)**; bare point estimates read as cherry-picked.
- **Organize by claim:** open each result subsection with a bolded one-line takeaway that could stand alone in the abstract. A reader skimming only the bold headers should absorb the thesis.
- Pair every aggregate number with a concrete anchor (absolute count beside the percentage, a named instance, a worked example).
- **Contamination control:** confirm strong scores are not driven by leakage (e.g., results on a held-out fresh split).

### 7.1 Case studies *(strongly recommended at security venues)*

Add 2-3 qualitative examples: **one success, one informative failure, one striking discovery**. These ground the quantitative results and are valued by security reviewers.

## 8. Discussion

- **Generalization:** does the finding hold beyond this sample, and why.
- **Limitations / threats to validity:** coverage gaps, settings not tested, ways the benchmark could be gamed or could saturate. Name the key limitation before a reviewer does.
- **Maintenance / versioning:** how the benchmark will be updated, how leakage will be managed over time, how submissions are evaluated.
- **Stakeholders:** what developers / platforms / evaluators should take from the results.

## 9. Ethics, responsible disclosure, and artifact

Make this visible from the table of contents.

- **Security venues:** sample handling, IRB/consent, redaction of sensitive content, and a responsible-disclosure paragraph naming who was notified and how they responded (if the benchmark exposes real vulnerabilities).
- **AI venues (e.g., NeurIPS):** a dedicated **Broader Impacts** statement.
- **Artifact:** public link (also in the abstract and intro) to the dataset, scoring harness, and an appendix with the full task list, prompts, and per-model breakdowns. State license and access conditions.

## 10. Conclusion

Under one column. Restate the headline number, name the broader implication, and gesture at future work in one sentence. Do not rehash construction, list subsections, or introduce new claims.

---

### Self-check before moving on
- [ ] All four ingredients concrete: task tuple, named-gate construction pipeline, operationally defined metrics, 3-5 justified baselines.
- [ ] Abstract leads with gap → name → scale → headline → takeaway.
- [ ] Novelty claim scoped with a qualified noun.
- [ ] Threat model placed per venue (standalone at security venues; inline at AI venues).
- [ ] Results organized by bolded takeaway claim; statistics paired with concrete anchors.
- [ ] Any automatic judge validated against ground truth on this task.
- [ ] Contamination/leakage addressed in at least one paragraph.
- [ ] Ethics/disclosure (or Broader Impacts) visible; public artifact linked in abstract and intro.

**Next**: `/research.analyze` to keep `claims.md` in sync with the findings above.
