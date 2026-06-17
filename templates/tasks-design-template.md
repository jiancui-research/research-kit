# System design & build plan: [project / paper short name]

> Produced by `/research.tasks`. Lives at `./.research/tasks/design.md`.
> The **design lane**: the system's architecture, how the repo is laid out, and the build
> task list. `/research.design` reads this and produces the actual **code** (in
> `~/Projects/<repo>`, outside the vault). This doc also doubles as the source for the
> paper's **System Design / Implementation** section, so keep the architecture honest.
>
> **Paper-type aware.** Heavy for systems/defense (a full architecture), medium for
> attack (a PoC / exploit) and benchmark (a construction harness). For **measurement /
> SoK** there is usually no system to build - skip this lane and keep any light
> data-obtain tasks in `tasks/experiment.md` instead.

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

## Repo layout & naming

[How the code repo is organized, so the design, experiment, and paper lanes all agree on
it. The experiment lane drops its scripts here; the paper's artifact section references it.]

- Repo: `~/Projects/[repo-name]` (outside the vault, never inside `.research/`).
- Folder structure:
  ```
  [repo-name]/
    src/            [the system itself]
    experiments/    [scripts the experiment lane adds]
    data/           [inputs / fixtures]
    README.md
  ```
- Naming conventions: [files / modules / experiment scripts - the shared rule everyone follows].

## Build task list

One task per component / artifact to construct. Name the deliverable and a done-when
criterion. Tag a heavy build `[spec-kit]` (warrants spec-driven development in its own
repo) or `[dev]` (normal development); light glue code needs no flag.

- [ ] [Component / deliverable] - done when [criterion]. [`[spec-kit]` / `[dev]`]
- [ ] ...

## Validate before building

- [ ] The diagram shows every component and the end-to-end path; nothing load-bearing is implicit.
- [ ] Each design decision names its rejected alternative (so the paper can defend it).
- [ ] Repo layout + naming are concrete enough that experiment scripts land in the right place.
- [ ] Every build task has a done-when criterion; heavy builds are flagged and point at a repo.
- [ ] For measurement / SoK: this lane is correctly skipped or kept minimal.

---
Next: `/research.design` (implement the build tasks into code), in parallel with
`/research.experiment` (evaluates the built system) and `/research.paper`.
