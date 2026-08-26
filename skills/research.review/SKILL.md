---
name: research.review
description: Self-review panel. Simulate reviewers reading ONLY the submitted paper, score it, and list specific findings each with a suggested fix command. Writes .research/review/round-N.md only; never edits the paper or any other artifact.
disable-model-invocation: true
---

> **research-kit stage - `/research.review`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.review.md` from this plugin's own directory - the folder two levels above
> this file - and follow it end to end. If you cannot find it, say so and stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage (optional focus (e.g. evaluation, related-work, a specific section) — omit for a full panel). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, run the `research.<x>` skill next.
>
> Everything else is unchanged: read and write only under `./.research/`, follow the
> command contract, and stay paper-type aware.
