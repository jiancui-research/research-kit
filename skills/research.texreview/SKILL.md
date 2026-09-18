---
name: research.texreview
description: "Open texreview, a local web UI to review the compiled paper - LaTeX source left, PDF right, SyncTeX click-to-source, comments on selections in either pane (button, `⌘⇧M`, or right-click) (requires uv + a TeX install). Comments are sidecar JSON in the paper repo's .texreview/ that any agent can read."
disable-model-invocation: true
---

> **research-kit stage - `/research.texreview`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.texreview.md` from this plugin's root - two directory levels above
> this skill's directory. Use that root as `<bundle>` for the command's Preparation
> and its `guides/`, `templates/`, and `tools/`. If it is missing, stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage (optional flags passed through, e.g. --main paper.tex --port 9000). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, suggest that skill next;
>   do not invoke it unless the user requested continuing to that stage.
>
> Follow the command's file and mode boundaries: tracking docs live in
> `./.research/`; code, evals, and manuscript files use their declared paths.
