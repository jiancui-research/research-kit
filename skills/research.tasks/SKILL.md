---
name: research.tasks
description: Derive the single work queue .research/tasks.md from plan.md - Setup/Build/Eval/Paper/Polish sections, T-ids, claim links; re-runs refine and preserve checkbox states.
disable-model-invocation: true
---

> **research-kit stage - `/research.tasks`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.tasks.md` from this plugin's own directory - the folder two levels above
> this file - and follow it end to end. If you cannot find it, say so and stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage (optional steering (e.g. "prioritize the kill-shot eval" or "paper tasks for sections 1-3 only")). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, run the `research.<x>` skill next.
>
> Everything else is unchanged: read and write only under `./.research/`, follow the
> command contract, and stay paper-type aware.
