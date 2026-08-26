---
name: research.style
description: Build and keep the writing-style file the writing commands read - distilled from papers you admire, the instructions you give, and the edits you make.
disable-model-invocation: true
---

> **research-kit stage - `/research.style`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.style.md` from this plugin's own directory - the folder two levels above
> this file - and follow it end to end. If you cannot find it, say so and stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage ((none) to refresh and to harvest this conversation, or an instruction to record now (e.g. "stop opening sections with 'In this section'")). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, run the `research.<x>` skill next.
>
> Everything else is unchanged: read and write only under `./.research/`, follow the
> command contract, and stay paper-type aware.
