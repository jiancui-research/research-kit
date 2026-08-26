---
name: research.proposal
description: Pipeline entry. Turn a raw research idea into proposal.md, a readable 1-3 page argument (falsifiable thesis, argued gap, pre-committed validation plan, venue + paper-type).
disable-model-invocation: true
---

> **research-kit stage - `/research.proposal`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.proposal.md` from this plugin's own directory - the folder two levels above
> this file - and follow it end to end. If you cannot find it, say so and stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage (a sentence or paragraph describing the rough idea (or steering to refine an existing proposal)). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, run the `research.<x>` skill next.
>
> Everything else is unchanged: read and write only under `./.research/`, follow the
> command contract, and stay paper-type aware.
