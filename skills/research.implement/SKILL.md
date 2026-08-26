---
name: research.implement
description: Work the tasks.md queue across Setup, Build, Eval, explicit user-led manuscript work, and Polish; keep claims and task status current.
disable-model-invocation: true
---

> **research-kit stage - `/research.implement`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.implement.md` from this plugin's own directory - the folder two levels above
> this file - and follow it end to end. If you cannot find it, say so and stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage (task id/section (e.g. T012, eval, or "paper intro"); Manuscript mode also accepts outline, critique, or explicit "draft <section>). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, run the `research.<x>` skill next.
>
> Everything else is unchanged: read and write only under `./.research/`, follow the
> command contract, and stay paper-type aware.
