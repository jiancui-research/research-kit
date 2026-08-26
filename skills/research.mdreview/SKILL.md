---
name: research.mdreview
description: Open mdreview, a local web UI for this repo's markdown: one wide pane you revise directly in the rendered view, or `split` for source beside preview. Comments are sidecar JSON in ./.mdreview/ that any agent can read (requires uv).
disable-model-invocation: true
---

> **research-kit stage - `/research.mdreview`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.mdreview.md` from this plugin's own directory - the folder two levels above
> this file - and follow it end to end. If you cannot find it, say so and stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage ((none) for the one-pane layout, `split` for source beside preview; any other flags pass through, e.g. `split --port 9000`). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, run the `research.<x>` skill next.
>
> Everything else is unchanged: read and write only under `./.research/`, follow the
> command contract, and stay paper-type aware.
