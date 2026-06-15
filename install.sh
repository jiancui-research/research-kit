#!/usr/bin/env sh
# Install speckit-research slash commands for one or more AI coding agents, and
# stage the bundled templates so /research.init can copy them into a paper repo.
#
# Supported agents:
#   claude    Claude Code slash commands  -> ~/.claude/commands/research.*.md
#   codex     Codex CLI custom prompts    -> ~/.codex/prompts/research.*.md
#   copilot   Copilot CLI custom agents   -> ~/.copilot/agents/research.*.agent.md
#
# Usage:
#   ./install.sh                      install for claude (default)
#   ./install.sh --copilot --codex    install for the named agents
#   ./install.sh --all                install for every supported agent
#   ./install.sh --symlink [agents]   symlink instead of copy (claude/codex only)
#   ./install.sh --uninstall          remove installed commands from all agents
#   ./install.sh --help               show this help
#
# POSIX sh only. Idempotent: re-running is safe and prints each action.
set -e

# Resolve this script's own directory so it works when invoked from anywhere.
SCRIPT_PATH="$0"
if [ -L "$SCRIPT_PATH" ]; then
    LINK_TARGET=$(readlink "$SCRIPT_PATH")
    case "$LINK_TARGET" in
        /*) SCRIPT_PATH="$LINK_TARGET" ;;
        *)  SCRIPT_PATH="$(dirname "$SCRIPT_PATH")/$LINK_TARGET" ;;
    esac
fi
SCRIPT_DIR=$(cd "$(dirname "$SCRIPT_PATH")" && pwd)

SRC_DIR="$SCRIPT_DIR/commands"

# Per-agent install destinations (override via environment if needed).
CLAUDE_DIR="${CLAUDE_COMMANDS_DIR:-$HOME/.claude/commands}"
CODEX_DIR="${CODEX_PROMPTS_DIR:-${CODEX_HOME:-$HOME/.codex}/prompts}"
COPILOT_DIR="${COPILOT_AGENTS_DIR:-$HOME/.copilot/agents}"

# Agent-neutral staging home for the bundled templates that /research.init copies in.
BUNDLE_HOME="${SPECKIT_RESEARCH_HOME:-$HOME/.speckit-research}"

usage() {
    sed -n '2,18p' "$SCRIPT_PATH" | sed 's/^# \{0,1\}//'
}

MODE=copy
AGENTS=""

add_agent() {
    case " $AGENTS " in
        *" $1 "*) ;;            # already selected
        *) AGENTS="$AGENTS $1" ;;
    esac
}

for arg in "$@"; do
    case "$arg" in
        --symlink)   MODE=symlink ;;
        --uninstall) MODE=uninstall ;;
        --all)       add_agent claude; add_agent codex; add_agent copilot ;;
        --claude)    add_agent claude ;;
        --codex)     add_agent codex ;;
        --copilot)   add_agent copilot ;;
        -h|--help)   usage; exit 0 ;;
        *)
            echo "error: unknown argument '$arg' (try --claude, --codex, --copilot, --all, --symlink, --uninstall, --help)" >&2
            exit 1
            ;;
    esac
done

# Default to Claude when no agent is named (backward compatible).
if [ -z "$AGENTS" ]; then
    AGENTS="claude"
fi

if [ ! -d "$SRC_DIR" ]; then
    echo "error: commands directory not found at $SRC_DIR" >&2
    exit 1
fi

# Collect the command files. Guard against the no-match glob case.
MATCHED=0
for src in "$SRC_DIR"/research.*.md; do
    [ -e "$src" ] || continue
    MATCHED=1
    break
done
if [ "$MATCHED" -eq 0 ]; then
    echo "error: no research.*.md commands found in $SRC_DIR" >&2
    exit 1
fi

# --- helpers -----------------------------------------------------------------

# Read the `description:` value from a command file's YAML frontmatter.
read_description() {
    awk '
        NR==1 && $0=="---" { infm=1; next }
        infm && $0=="---"  { exit }
        infm && /^description:/ {
            sub(/^description:[ \t]*/, "")
            print
            exit
        }
    ' "$1"
}

# Print a command file body (everything after the closing frontmatter ---).
read_body() {
    awk '
        /^---[ \t]*$/ && fm < 2 { fm++; next }
        fm >= 2 { print }
    ' "$1"
}

# Copy or symlink the raw command markdown into a destination directory.
# Used for agents that consume the Claude/Codex command format verbatim.
install_raw() {
    agent="$1"
    dest="$2"
    mkdir -p "$dest"
    echo "Installing speckit-research commands for $agent into $dest ($MODE)"
    for src in "$SRC_DIR"/research.*.md; do
        [ -e "$src" ] || continue
        name=$(basename "$src")
        target="$dest/$name"
        [ -e "$target" ] || [ -L "$target" ] && rm -f "$target"
        if [ "$MODE" = symlink ]; then
            ln -s "$src" "$target"
            echo "  linked   $target -> $src"
        else
            cp "$src" "$target"
            echo "  copied   $target"
        fi
    done
}

# Transform each command into a Copilot CLI custom agent (*.agent.md).
# Copilot agents are personas selected via /agent, not parameterized slash
# commands, so we prepend an adapter note that maps the slash-command idioms
# ($ARGUMENTS, "Next: /research.x") onto the agent model.
install_copilot() {
    dest="$COPILOT_DIR"
    mkdir -p "$dest"
    echo "Installing speckit-research commands for copilot into $dest (generated agents)"
    for src in "$SRC_DIR"/research.*.md; do
        [ -e "$src" ] || continue
        base=$(basename "$src" .md)          # e.g. research.idea
        target="$dest/$base.agent.md"
        desc=$(read_description "$src")
        [ -e "$target" ] || [ -L "$target" ] && rm -f "$target"
        {
            echo "---"
            echo "name: $base"
            echo "description: \"$desc\""
            echo "---"
            echo
            echo "> **speckit-research agent.** You are the \`$base\` stage of the speckit-research"
            echo "> pipeline, packaged as a GitHub Copilot CLI custom agent. Two adaptations from the"
            echo "> original slash-command form:"
            echo ">"
            echo "> - Wherever the steps below reference \`\$ARGUMENTS\`, treat it as the user's latest"
            echo ">   message to you (their free-text input for this stage). If it is empty, follow the"
            echo ">   step's \"if empty\" guidance."
            echo "> - Wherever a step ends with \`Next: /research.<x>\`, it means: switch to the"
            echo ">   \`research.<x>\` agent (via \`/agent\`) for the next stage."
            echo ">"
            echo "> Everything else is unchanged: read and write only under \`./.research/\`, follow the"
            echo "> command contract, and stay paper-type aware."
            echo
            read_body "$src"
        } > "$target"
        echo "  generated $target"
    done
}

install_agent() {
    case "$1" in
        claude)  install_raw claude "$CLAUDE_DIR" ;;
        codex)   install_raw codex  "$CODEX_DIR" ;;
        copilot) install_copilot ;;
    esac
}

stage_templates() {
    if [ -d "$SCRIPT_DIR/templates" ]; then
        mkdir -p "$BUNDLE_HOME"
        rm -rf "$BUNDLE_HOME/templates"
        cp -R "$SCRIPT_DIR/templates" "$BUNDLE_HOME/templates"
        echo "  staged   $BUNDLE_HOME/templates (bundled templates for /research.init)"
    fi
}

uninstall_dir() {
    agent="$1"
    dest="$2"
    pattern="$3"
    echo "Uninstalling speckit-research commands for $agent from $dest"
    found=0
    for f in "$dest"/$pattern; do
        if [ -e "$f" ] || [ -L "$f" ]; then
            rm -f "$f"
            echo "  removed  $f"
            found=1
        fi
    done
    [ "$found" -eq 0 ] && echo "  skip     (nothing installed in $dest)"
    return 0
}

# --- main --------------------------------------------------------------------

if [ "$MODE" = uninstall ]; then
    uninstall_dir claude  "$CLAUDE_DIR"  "research.*.md"
    uninstall_dir codex   "$CODEX_DIR"   "research.*.md"
    uninstall_dir copilot "$COPILOT_DIR" "research.*.agent.md"
    if [ -d "$BUNDLE_HOME" ]; then
        rm -rf "$BUNDLE_HOME"
        echo "  removed  $BUNDLE_HOME (staged templates)"
    fi
    echo "Done."
    exit 0
fi

for agent in $AGENTS; do
    install_agent "$agent"
done

# Stage the bundled templates once, regardless of how many agents were installed.
stage_templates

echo "Done. In your paper repo, run /research.init once, then /research.constitution."
