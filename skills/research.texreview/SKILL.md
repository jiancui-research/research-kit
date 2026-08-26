---
name: research.texreview
description: Open texreview, a local web UI to review the compiled paper - LaTeX source left, PDF right, SyncTeX click-to-source, comments on PDF selections (requires uv + a TeX install). Comments are sidecar JSON in the paper repo's .texreview/ that any agent can read.
disable-model-invocation: true
---

> **research-kit stage - `/research.texreview`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.texreview.md` from this plugin's own directory - the folder two levels above
> this file - and follow it end to end. If you cannot find it, say so and stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage (optional flags passed through, e.g. --main paper.tex --port 9000). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, run the `research.<x>` skill next.
>
> Everything else is unchanged: read and write only under `./.research/`, follow the
> command contract, and stay paper-type aware.
