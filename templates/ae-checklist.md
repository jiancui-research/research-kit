# Artifact-evaluation (AE) checklist

A template for preparing a research artifact (code, data, models, proofs) for an
artifact-evaluation track. Fill each section in `.research/ae/`. The goal is that
an independent evaluator, with only your README and your archived artifact, can
reach the badge you are claiming. Be explicit, be honest, and assume the
evaluator has none of your context.

> Badges are earned, not requested. Claim only the badge your artifact actually
> supports, and make the reviewer's job mechanical: clear steps, exact commands,
> expected outputs.

---

## 1. Badge target

State which badge(s) you are going for and why each is justified. Most tracks
offer three (names vary by venue, but the substance is consistent):

| Badge | What it means | What you must provide |
| --- | --- | --- |
| **Available** | The artifact is publicly retrievable and permanently archived. | A stable, citable link (DOI / archival URL). No functionality claim. |
| **Functional** | The artifact is complete, documented, exercisable, and does what the paper says (it runs and produces sane output). | Build/run instructions + a way to exercise the core code paths. |
| **Reproduced** | An independent party reproduced the paper's central results from the artifact. | The above, plus a mapping from paper claims to runnable experiments and expected numbers. |

Write one line per badge: `Available: <yes/no + link>`, `Functional: <yes/no +
which run proves it>`, `Reproduced: <yes/no + which claims are reproducible and
which are not, with reason>`.

---

## 2. Archival link (Available badge)

Available is the easiest to lose on a technicality. Confirm all of:

- [ ] The artifact has a **permanent, immutable** archive (e.g. a DOI-issuing
      repository or a versioned release snapshot), not just a mutable branch.
- [ ] The link is **public** and resolves from a clean machine / incognito
      session with no login.
- [ ] The archived snapshot **matches** the version your paper describes (tag or
      commit recorded in the README).
- [ ] You **archived early**, not at the deadline - a last-minute snapshot risks
      archiving a version that differs from the paper. Freeze and verify with time
      to spare.
- [ ] A development mirror (if any) is clearly separated from the archived,
      citable copy so reviewers know which one to evaluate.
- [ ] The license is present and permits evaluation and reuse (see Section 5).

> A live code-host URL alone usually does NOT satisfy Available - its content can
> change or disappear. Pair it with an archival snapshot that has a DOI or
> equivalent permanent identifier.

---

## 3. Artifact README contents (Functional badge)

The README is the artifact's user manual and the document the evaluator reads
first. It should stand alone. Include, in order:

- [ ] **Overview** - one paragraph: what the artifact is and which paper it
      backs.
- [ ] **Claims supported** - bullet list of the paper claims this artifact
      backs, each pointing at the experiment that demonstrates it (links to
      Section 4).
- [ ] **Directory layout** - what lives where (code, data, scripts, results).
- [ ] **Requirements** - OS, hardware (CPU/GPU/RAM/disk), required accounts or
      external services, and any resource that is NOT bundled.
- [ ] **Setup** - exact, copy-pasteable install steps; prefer a pinned
      environment (lockfile / container image / dependency manifest with
      versions). State expected setup time.
- [ ] **Smoke test** - one short command that proves the artifact runs in
      minutes, so the evaluator confirms basic functionality before the long
      runs.
- [ ] **Usage** - how to run the main entry points, with example invocations.
- [ ] **Experiment-to-claim map** - see Section 4.
- [ ] **Expected output** - what success looks like (sample output, expected
      files, expected numbers / tolerances).
- [ ] **Runtime & cost** - wall-clock and resource cost for each experiment, so
      reviewers can plan and abort-budget long jobs.
- [ ] **Troubleshooting** - known failure modes and fixes.
- [ ] **License & citation** - how to cite, under what license.

---

## 4. Reproducibility steps (Reproduced badge)

Reproduced is about a stranger getting your numbers. Provide a path from each
central claim to a command and an expected result.

- [ ] **Claim-to-experiment table.** For each headline result, give: the claim,
      the figure/table in the paper, the exact script/command, the expected
      output, and the acceptable tolerance. (Reuse `.research/claims.md`.)

      `Claim -> Paper Table/Fig -> Command -> Expected value (± tolerance) -> Runtime`

- [ ] **One-command-per-result where possible.** Wrap multi-step pipelines in a
      single script per claim; avoid forcing the evaluator to assemble steps.
- [ ] **Determinism.** Pin seeds, versions, and data snapshots. Where results are
      inherently stochastic, say so and report expected variance, not a single
      magic number.
- [ ] **Tolerances stated.** Hardware and library differences shift numbers
      slightly; give the range that still counts as a reproduction.
- [ ] **Scope honesty.** If some results need infeasible resources (huge compute,
      restricted data, long training), provide a **scaled-down or cached**
      reproduction path AND clearly mark which full results are not
      independently reproducible and why.
- [ ] **Data availability.** Bundle or fetch-script the data; if data cannot be
      shared (privacy/license), document the substitute and what it can show.
- [ ] **End-to-end dry run.** You (or a colleague with no context) ran every step
      on a clean machine and reached the expected outputs. Have the outsider follow
      the README verbatim, so hidden steps, hard-coded paths, and author-only
      knowledge surface before the evaluator hits them.

---

## 5. Licensing, ethics, and access

- [ ] License file included and compatible with reuse and the dependencies you
      ship.
- [ ] Third-party data/models redistributed only where permitted; otherwise a
      documented fetch step.
- [ ] No secrets, credentials, API keys, or private/personal data committed.
- [ ] Human-subjects or sensitive data handled per the paper's ethics statement
      (approval and access conditions noted).
- [ ] Any required external service/account that the evaluator must obtain is
      called out up front, with cost and access friction.

---

Output to `.research/ae/`. Next: `/research.review` to self-review the paper, or
revisit `/research.experiment` to keep the claim-evidence matrix in sync.
