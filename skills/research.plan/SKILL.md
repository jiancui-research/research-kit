---
name: research.plan
description: "Design the study and maintain its work queue in .research/plan.md and .research/tasks.md, preserving task IDs and progress."
disable-model-invocation: true
---

> **research-kit stage - `/research.plan`.**
>
> The instructions for this stage are not duplicated here. Read
> `commands/research.plan.md` from this plugin's root - two directory levels above
> this skill's directory. Use that root as `<bundle>` for the command's Preparation
> and its `guides/`, `templates/`, and `tools/`. If it is missing, stop rather
> than reconstructing the stage from memory.
>
> Two adaptations from its original slash-command form:
>
> - Where it references `$ARGUMENTS`, that means the user's latest message to you -
>   their free-text input for this stage (optional design or queue steering (e.g. "coverage over severity", "prioritize the decisive eval", "refresh tasks from the existing plan")). When they gave none, follow the
>   step's "if empty" guidance or ask for it; never invent one.
> - Where a step ends with `Next: /research.<x>`, suggest that skill next;
>   do not invoke it unless the user requested continuing to that stage.
>
> Follow the command's file and mode boundaries: tracking docs live in
> `./.research/`; code, evals, and manuscript files use their declared paths.
