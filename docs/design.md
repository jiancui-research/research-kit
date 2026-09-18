# Research-kit design

## Purpose and public surface

Research-kit is a bundle of agent instructions for developing research, running a
study, and writing a paper. The model performs the work; Markdown defines the
procedures and reviewable artifacts. The two optional Python viewers provide local
editing and commenting without becoming dependencies of the research pipeline.

The nine commands are `proposal`, `relatedwork`, `feasibility`, `plan`, `implement`,
`write`, `review`, `mdreview`, and `texreview`, all under `/research.*`.

```text
proposal -> relatedwork -> feasibility -> plan -> implement -> write -> review
   ^                         |                 ^                ^         |
   +------ NO-GO/PIVOT -------+                 +---- findings --+---------+
```

The writing path is independently usable with an existing manuscript. Both viewers
remain separate leaf utilities. No generic dispatcher replaces them.

## One command source, several adapters

`commands/research.<name>.md` is the authoritative instruction source. Claude Code
and OMP plugins expose these commands directly. `tools/gen_codex_skills.py` generates
`.codex-plugin/plugin.json` and `skills/<name>/SKILL.md`; each skill points back to
its command and identifies the enclosing bundle root. It does not duplicate the
procedure. Generate again whenever a command or the manifest changes.

`install.sh` copies raw command files for Claude/Codex custom-prompt installs and
creates Copilot custom agents with an input adapter. It stages `guides/`,
`templates/`, and `tools/` together. Its recorded install manifests let an upgrade
prune retired stages without guessing ownership of user-created commands.

Adapters preserve the command's actual file/mode boundaries, including code and
manuscripts outside `.research/`. `Next:` is a suggestion, not automatic execution.
Generated skills retain `disable-model-invocation: true` for hosts that support it;
each skill also has `agents/openai.yaml` with Codex's
`policy.allow_implicit_invocation: false`. Command bodies independently require
explicit selection for manuscript work. String frontmatter is quoted so colons
and quotation marks survive YAML parsing in every adapter.

The local Codex loader accepts the shared Claude guard. The universal catalog
validator rejects that field when true, so a successful local installation is
not a catalog-submission validation. Keep this distinction explicit when checking
distribution compatibility.
See [installation](install.md) for invocation and update instructions.

## Internal procedures and local customization

Four procedures live in the bundle's `guides/` directory:

| Procedure | Loaded by | Responsibility |
|---|---|---|
| `setup.md` | Every command; viewers take its resource-only branch | Missing templates and project preferences |
| `task-planning.md` | `plan` | Derive/refine the queue without losing progress |
| `writing-style.md` | `write`; explicit manuscript work in `implement` | Example selection or explicit skip, sample analysis, standing instructions, confirmed edit preferences |
| `consistency.md` | `implement`, `write` | Check affected claims, evidence, code, tasks, and prose |

Procedures are always read from the installed bundle so an upgrade reaches them.
Customizable templates and craft guides are copied with no clobber into
`.research/templates/`. Setup compares relevant copies, reports drift, and preserves
local edits. It cannot attribute a diff to the user or an update without a baseline.
Required missing guidance is a blocker; optional missing guidance is named.

The example-paper decision is required before outlining, drafting, or revising;
users can explicitly skip it. Both writing entry points load the bundled procedure
directly, so an older local manuscript template cannot bypass the decision. The
same `writing/style.md` records the choice, its scope, and the selected sources and
lessons. A project-wide skip survives later runs and sample refreshes; a skip for
one request does not become a permanent preference. Critiques and checks need no
examples. Recommendations require verified sources and concrete writing lessons,
and become selected examples only when the user chooses them.

Old local templates can still mention retired stages. Setup translates those
handoffs to current owners. It never deletes old project outputs or overrides
current command boundaries to satisfy an old template.

## File ownership

```text
project/
  .research/
    memory/constitution.md   project preferences, seeded automatically
    templates/               local skeletons and craft
    writing/style.md         example choice, analysis, and writing preferences
    writing/samples/         local example papers (links/paths also accepted)
    proposal.md              argument and claim IDs
    related-work.md          survey and positioning
    feasibility.md           probe and verdict
    plan.md                  study design
    tasks.md                 queue with stable IDs and progress
    claims.md                claim-to-evidence ledger
    review/round-N.md         paper-only review reports
    paper-repo               optional manuscript path and URL
  feasibility/               probe code
  src/                       implementation, or the plan's declared location
  eval/                      scripts, results, writeups, and index
  paper/                     manuscript, or an existing separate repo
```

`plan` owns both design and queue creation/refinement. `implement` records progress,
claim verdicts, and built-design deviations; its explicit Paper mode additionally
updates the selected manuscript task. `write` leaves the queue alone.
`relatedwork` may sharpen proposal positioning. Requested writing preferences go
into the existing style file. Consistency checks report broader work instead of
silently editing unrelated artifacts.

After shared setup, `review` writes only its round file. It reads the manuscript
and venue/type context without internal project evidence. This boundary is what
makes it a useful simulation of an outside reader.

## Scope

Keep the full research loop and the specialized writing/review craft. Automatic
setup, queue derivation, style learning, and consistency checks do not need public
commands of their own. Standalone response-to-reviewer and artifact-submission
commands are removed; their old project outputs are left alone.

There is no orchestration daemon, pipeline CLI, or automatic publication step.
Changes to the public surface must update the adapters, documentation, and handoffs
as one change. Tests cover packaging and the viewers; prompt behavior also needs
representative runs in throwaway projects. Never use a personal research repo as
a test fixture.
