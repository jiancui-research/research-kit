# research-kit workflow

The pipeline and the input/output of every command. (See the [README](../README.md) for install + quickstart.)

## Diagram

```mermaid
flowchart TD
    C["constitution (one-time)<br/>writes memory/constitution.md"]
    I(["your raw idea"])
    P["proposal<br/>writes proposal.md"]
    RW["relatedwork<br/>writes related-work.md"]
    F{"feasibility<br/>writes feasibility.md<br/>GO / NO-GO / PIVOT"}
    T["tasks<br/>writes tasks/design.md + tasks/experiment.md + tasks/paper.md"]
    D["design<br/>builds code in ./design/"]
    E["experiment<br/>writes experiments/"]
    PA["paper (human-led)<br/>writes paper/"]
    AN["analyze (+ sync checker)<br/>writes analyze-report.md"]
    RV["review (loop)<br/>writes review/round-N.md"]
    CL[("claims.md")]

    C -.->|"read first by every command"| P
    I --> P
    P --> RW
    RW --> F
    RW -.->|"sharpens"| P
    F -->|"GO"| T
    F -->|"NO-GO / PIVOT"| P
    T --> D
    T --> E
    T --> PA
    D -.->|"built system"| E
    D -.->|"System Design section"| PA
    E -.->|"fills"| CL
    CL -.->|"reads"| PA
    D --> AN
    E --> AN
    PA --> AN
    AN -.->|"re-run stale lane"| D
    AN -.->|"re-run stale lane"| E
    AN -.->|"re-run stale lane"| PA
    AN --> RV
    RV -.->|"auto-appends tasks"| T
    RV -.->|"re-run after fixes"| RV
```

**Reading it:** solid arrows are the pipeline flow; dashed arrows are cross-document reads, updates, and loops. `feasibility` is a GO/NO-GO/PIVOT gate (a NO-GO or PIVOT loops back to `proposal`). After a GO, `tasks` fans out into **three parallel lanes** — `design` (builds the system as code in `./design/`), `experiment` (evaluates it, filling `claims.md`), and `paper` (human-led writing) — which co-evolve rather than run in sequence. `analyze` is the **sync checker**: it detects when one lane drifts from the others and routes the exact re-run, and it doubles as the review-readiness audit. `review` is a **loop** — re-run after fixes until no high-severity findings remain. Auxiliary commands `rebuttal` (post-submission) and `ae` (artifact evaluation) run as needed. The design lane is paper-type aware: heavy for systems/defense, skipped for measurement / SoK.

## Input → output, per command

All research-kit **tracking docs** live under `./.research/`; the actual **work products** (code, data, paper source) live in sibling root folders — `feasibility/`, `design/`, `experiment/`, `paper/`. The whole project is one repo under `~/Projects`, outside the vault.

| Command | Reads (input) | Writes (new) | Updates (existing) |
| --- | --- | --- | --- |
| `constitution` | your focus areas | `memory/constitution.md` | itself on re-run |
| `proposal` | your raw idea | `proposal.md` | itself on re-run |
| `relatedwork` | `proposal.md` | `related-work.md` | **`proposal.md`** (sharpens gap/positioning) |
| `feasibility` | `proposal.md` (+ `related-work.md`) | `feasibility.md` | — |
| `tasks` | `proposal.md` + `feasibility.md` | `tasks/design.md`, `tasks/experiment.md`, `tasks/paper.md` | — |
| `design` (build) | `tasks/design.md` | **code in `./design/`** | `tasks/design.md` (build status) |
| `experiment` | `tasks/experiment.md` | `experiments/NN-*.md`, `experiments/index.md` | **`claims.md`** |
| `paper` (human-led) | `tasks/paper.md`, `tasks/design.md`, `proposal`, `related-work`, `claims.md` | `paper/<section>.md` | `tasks/paper.md` (status) |
| `analyze` (+ sync) | everything (read-only) | `analyze-report.md` | — (routes re-runs) |
| `review` (loop) | `proposal`, `related-work`, `claims`, `paper` | `review/round-N.md` | **`tasks/experiment.md`** (auto-appends) |
| `rebuttal` (aux) | reviewer comments | `rebuttal/rebuttal.md` | — |
| `ae` (aux) | `claims`, `tasks`, `experiments` | `ae/*` | — |

### Write-edges, and how the three lanes talk

Only three commands ever **write into another command's document** — the feedback that makes this a workflow rather than a one-way chain:

1. **`relatedwork` → `proposal.md`** — the survey sharpens the gap and positioning.
2. **`experiment` → `claims.md`** — results fill the claim ↔ evidence matrix.
3. **`review` → `tasks/experiment.md`** — evidence-gap findings become new experiment tasks.

The three lanes (`design ∥ experiment ∥ paper`) stay decoupled because they communicate **only through shared documents they read, never write into each other**:

- `design` writes its **code** (own repo) and `tasks/design.md` (own status); `experiment` and `paper` *read* `tasks/design.md` (the system spec, and the source for the System Design section).
- `experiment` writes `claims.md`; `paper` *reads* it and tags any unbacked claim `[UNVERIFIED]`.
- `analyze` is read-only: when a lane drifts, it does not edit the others — it **routes the re-run** (`design changed → re-run experiment NN + paper system-design`) so each owning command re-syncs its own artifact. That is the sync mechanism: detect with `analyze`, reflect by re-running the owner.

## Task surfaces

The actual *doing* lives in four separate places, each scoped to its job — don't confuse them:

| task surface | where | scope | feeds |
| --- | --- | --- | --- |
| **feasibility probe** | `feasibility.md` (Probe plan) | throwaway de-risk | the GO/NO-GO verdict |
| **design / build tasks** | `tasks/design.md` | build the system (→ code) | `/research.design` → `./design/` + System Design section |
| **experiment tasks** | `tasks/experiment.md` | rigorous evaluation | `claims.md` → the paper |
| **paper tasks** | `tasks/paper.md` | writing | the draft |

The feasibility probe keeps its own short checklist inside `feasibility.md` and deliberately does **not** enter `claims.md`. The design lane is paper-type aware: present for build-papers (systems / defense / attack / benchmark), skipped for measurement / SoK (any light data-obtain stays in `tasks/experiment.md`).

## Examples

Measurement paper (no design lane):

```text
/research.proposal     LLM agents leak secrets via tool-call arguments; measure how often
/research.relatedwork  group by attack vs defense; closest baseline is GuardAgent
/research.feasibility  just find 5 real leak instances by hand first
/research.tasks
/research.experiment   run the baseline comparison
/research.paper intro            # outline (default; you write the prose)
/research.paper draft eval       # full prose (opt-in)
/research.analyze
/research.review evaluation      # one lens, or omit for the full panel
```

Systems / defense paper (the design lane builds the system):

```text
/research.tasks
/research.design                 # implement the architecture into ./design/
/research.experiment             # evaluate the built system, fill claims.md
/research.paper system-design    # outline the section from tasks/design.md
/research.analyze sync           # after a design change: what's stale + what to re-run
```
