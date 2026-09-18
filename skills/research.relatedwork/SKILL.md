---
name: research.relatedwork
description: "Survey prior work into .research/related-work.md AND sharpen the proposal's gap and positioning."
disable-model-invocation: true
---

> **research-kit stage - `/research.relatedwork`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.relatedwork.md` from this plugin's root - two directory levels above
> this skill's directory. Use that root as `<bundle>` for the command's Preparation
> and its `guides/`, `templates/`, and `tools/`. If it is missing, stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage (optional pointers to key prior work, themes, or the closest baselines). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, suggest that skill next;
>   do not invoke it unless the user requested continuing to that stage.
>
> Follow the command's file and mode boundaries: tracking docs live in
> `./.research/`; code, evals, and manuscript files use their declared paths.
