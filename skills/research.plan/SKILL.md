---
name: research.plan
description: Turn the proposal + feasibility into the study's technical design at .research/plan.md - architecture, evaluation design, key decisions, project layout. Stable; tasks derive from it.
disable-model-invocation: true
---

> **research-kit stage - `/research.plan`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.plan.md` from this plugin's own directory - the folder two levels above
> this file - and follow it end to end. If you cannot find it, say so and stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage (optional steering (e.g. "security venue, coverage over severity" or "code goes in ./src/core")). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, run the `research.<x>` skill next.
>
> Everything else is unchanged: read and write only under `./.research/`, follow the
> command contract, and stay paper-type aware.
