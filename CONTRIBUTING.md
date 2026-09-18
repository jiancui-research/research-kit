# Contributing to research-kit

Research-kit is an MIT-licensed bundle of agent commands, guides, and templates,
with two optional local review UIs. Keep changes focused and the public surface small.

## Conventions

- **One source:** author commands in `commands/research.<name>.md`. Generated Codex
  skills and Copilot agents adapt those files; never maintain a second copy by hand.
- **Nine public commands:** proposal, relatedwork, feasibility, plan, implement,
  write, review, mdreview, texreview. Keep the two viewers separate.
- **Internal work:** setup, task derivation, style learning, and consistency checks
  live in `guides/` and are loaded by the public commands that own the work.
- **User customization:** templates are copied into `.research/templates/` without
  clobbering existing copies. Project preferences stay in
  `.research/memory/constitution.md`; writing preferences stay in `.research/writing/style.md`.
- **State preservation:** `plan` maintains design and queue in separate files.
  Preserve task IDs, checkboxes, notes, and dependency history. Sample refreshes
  preserve the style file's user-owned sections.
- **Execution boundaries:** implementation runs automated queue tasks by default;
  Paper tasks require explicit selection. Writing reads the whole manuscript first.
  Review reads only the paper and venue context. Next-step suggestions never execute themselves.
- **Original guidance:** distill general patterns, not private notes, identifiable
  drafts, or someone else's sentences. Keep examples synthetic.

## Editing commands or guides

1. Use minimal YAML frontmatter with `description` and optional `argument-hint`.
   User input arrives through `$ARGUMENTS` or the adapter's invoking message.
2. Keep command files under about 120 lines and follow their Preparation step.
   Internal guides come from the installed bundle; artifact templates come from
   the user's local `.research/templates/` copies.
3. Update the README command table, `docs/workflow.md`, `docs/design.md`, and any
   affected templates or handoffs together. Do not leave references to removed commands.
4. Bump `.claude-plugin/plugin.json` for meaningful bundle changes and run
   `python3 tools/gen_codex_skills.py`. The generated Codex manifest follows it.
5. Preserve command ownership: `plan` owns design and queue; `implement` updates
   progress/evidence; `write` leaves the queue alone; `review` writes only a round
   after automatic setup. See the workflow document for details.

## Validation

```sh
uv run --with pytest --with markdown-it-py --with pyyaml pytest tools
```

The tests cover viewer code and packaging, including generated skills and isolated
installer upgrades. For manual install checks, point `CLAUDE_COMMANDS_DIR`,
`CODEX_PROMPTS_DIR`, `COPILOT_AGENTS_DIR`, and `RESEARCH_KIT_HOME` at dedicated
throwaway directories. Run install, repeat install, and uninstall there. Never
uninstall a user's real tools as a test.

For prompt changes, also exercise representative requests in a synthetic paper
project: a new proposal, a plan with an existing queue, standalone writing/style
work, a paper-only review, and both viewer launch paths. Automated packaging checks
do not establish that an agent followed a prompt correctly.

Keep the optional viewers as leaf utilities. Pipeline commands must remain usable
without either viewer, and no daemon or orchestration service is needed.
