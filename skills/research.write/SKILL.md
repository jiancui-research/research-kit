---
name: research.write
description: Write or revise one manuscript section - reads the whole paper and states its argument before any prose, then outlines, revises, critiques, or drafts.
disable-model-invocation: true
---

> **research-kit stage - `/research.write`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.write.md` from this plugin's own directory - the folder two levels above
> this file - and follow it end to end. If you cannot find it, say so and stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage (section, optionally with a mode (e.g. "related-work", "revise eval - the ASR moved to 31%", "draft intro")). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, run the `research.<x>` skill next.
>
> Everything else is unchanged: read and write only under `./.research/`, follow the
> command contract, and stay paper-type aware.
