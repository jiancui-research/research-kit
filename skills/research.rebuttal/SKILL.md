---
name: research.rebuttal
description: Draft a prioritized, evidence-backed rebuttal to reviewer comments into .research/rebuttal/, fitted to the venue word limit.
disable-model-invocation: true
---

> **research-kit stage - `/research.rebuttal`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.rebuttal.md` from this plugin's own directory - the folder two levels above
> this file - and follow it end to end. If you cannot find it, say so and stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage (paste the reviews, or pass a path to a file with them (e.g. "reviews.txt, 600-word limit, one reviewer is borderline-positive")). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, run the `research.<x>` skill next.
>
> Everything else is unchanged: read and write only under `./.research/`, follow the
> command contract, and stay paper-type aware.
