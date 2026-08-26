---
name: research.ae
description: Prepare an artifact-evaluation submission (reproducibility checklist, artifact README, badge plan, permanent archival link).
disable-model-invocation: true
---

> **research-kit stage - `/research.ae`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.ae.md` from this plugin's own directory - the folder two levels above
> this file - and follow it end to end. If you cannot find it, say so and stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage (optional — venue (e.g. usenix, acm), badge targets, or notes about what the artifact contains). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, run the `research.<x>` skill next.
>
> Everything else is unchanged: read and write only under `./.research/`, follow the
> command contract, and stay paper-type aware.
