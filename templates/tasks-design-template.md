# System design & build plan: [project / paper short name]

> Produced by `/research.tasks`. Lives at `./.research/tasks/design.md`.
> The **design lane**: the system's architecture, the project layout, and the build task
> list. `/research.design` reads this and produces the actual **code** in the project's
> `./design/` folder (a sibling of `.research/`; the project is one repo under
> `~/Projects`, outside the vault). This doc also doubles as the source for the paper's
> **System Design / Implementation** section, so keep the architecture honest.
>
> **Paper-type aware.** Heavy for systems/defense (a full architecture), medium for
> attack (a PoC / exploit) and benchmark (a construction harness). For **measurement /
> SoK** there is usually no system to build - skip this lane and keep any light
> data-obtain tasks in `tasks/eval.md` instead.

## System overview (the design picture)

[The architecture in one paragraph, then a diagram. What the system is, the components it
has, and how data / control flows between them. Show the smallest end-to-end path first.]

```
[ASCII or mermaid workflow diagram: components + arrows, e.g.
  input ──▶ [ component A ] ──▶ [ component B ] ──▶ output ]
```

- **Components.** [one line each: name -> responsibility]
- **Data / control flow.** [the main path through the components, end to end]

## Key design decisions & rationale

[The load-bearing choices a reviewer will question. For each: the decision, why, and the
alternative you rejected. This is exactly what the paper's design section has to defend.]

- Decision: [...] - chosen because [...]; rejected [alternative] because [...].

## Project layout & naming

[How the project is organized so every lane agrees on it. research-kit's tracking docs
live in `.research/`; the actual work products live in sibling root folders. The system
code is built into `./design/`.]

- Project root: `~/Projects/[project]/` (one repo, outside the vault).
- Layout:
  ```
  [project]/
    .research/      [all research-kit tracking docs — proposal, tasks, claims, ...]
    feasibility/    [throwaway probe code]
    design/         [THE SYSTEM CODE — what /research.design builds]
      src/  ...     [internal structure: modules / entrypoints]
    eval/     [evaluation scripts, data, results]
    paper/          [manuscript; often a dedicated sibling repo <name>-<venue><yy>-latex
                     recorded in .research/paper-repo - resolved by /research.paper]
  ```
- `design/` internal structure: [src / modules / entrypoints].
- Naming conventions: [the shared rule for files, modules, and eval scripts].

## Build task list

One task per component / artifact to construct. Name the deliverable and a done-when
criterion. Tag a heavy build `[spec-kit]` (warrants spec-driven development in its own
repo) or `[dev]` (normal development); light glue code needs no flag.

- [ ] [Component / deliverable] - done when [criterion]. [`[spec-kit]` / `[dev]`]
- [ ] ...

## Validate before building

- [ ] The diagram shows every component and the end-to-end path; nothing load-bearing is implicit.
- [ ] Each design decision names its rejected alternative (so the paper can defend it).
- [ ] Project layout + naming are concrete enough that eval scripts land in the right place.
- [ ] Every build task has a done-when criterion; heavy builds are flagged and point at a repo.
- [ ] For measurement / SoK: this lane is correctly skipped or kept minimal.

---
Next: `/research.design` (implement the build tasks into code), in parallel with
`/research.eval` (evaluates the built system) and `/research.paper`.
