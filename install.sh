#!/usr/bin/env sh
# Install speckit-research slash commands into ~/.claude/commands/, and stage the
# bundled templates into ~/.claude/speckit-research/ so /research.init can copy
# them into a paper repo.
#
# Usage:
#   ./install.sh              copy commands + stage templates
#   ./install.sh --symlink    symlink the commands instead of copying
#   ./install.sh --uninstall  remove installed commands and staged templates
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
DEST_DIR="${CLAUDE_COMMANDS_DIR:-$HOME/.claude/commands}"
BUNDLE_HOME="${SPECKIT_RESEARCH_HOME:-$HOME/.claude/speckit-research}"

MODE=copy
for arg in "$@"; do
    case "$arg" in
        --symlink)   MODE=symlink ;;
        --uninstall) MODE=uninstall ;;
        -h|--help)
            sed -n '2,9p' "$SCRIPT_PATH" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "error: unknown argument '$arg' (try --symlink, --uninstall, --help)" >&2
            exit 1
            ;;
    esac
done

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

if [ "$MODE" = uninstall ]; then
    echo "Uninstalling speckit-research commands from $DEST_DIR"
    for src in "$SRC_DIR"/research.*.md; do
        [ -e "$src" ] || continue
        name=$(basename "$src")
        dest="$DEST_DIR/$name"
        if [ -e "$dest" ] || [ -L "$dest" ]; then
            rm -f "$dest"
            echo "  removed  $dest"
        else
            echo "  skip     $dest (not present)"
        fi
    done
    if [ -d "$BUNDLE_HOME" ]; then
        rm -rf "$BUNDLE_HOME"
        echo "  removed  $BUNDLE_HOME (staged templates)"
    fi
    echo "Done."
    exit 0
fi

mkdir -p "$DEST_DIR"
echo "Installing speckit-research commands into $DEST_DIR ($MODE)"
for src in "$SRC_DIR"/research.*.md; do
    [ -e "$src" ] || continue
    name=$(basename "$src")
    dest="$DEST_DIR/$name"
    # Remove any existing file/symlink so the install is idempotent.
    [ -e "$dest" ] || [ -L "$dest" ] && rm -f "$dest"
    if [ "$MODE" = symlink ]; then
        ln -s "$src" "$dest"
        echo "  linked   $dest -> $src"
    else
        cp "$src" "$dest"
        echo "  copied   $dest"
    fi
done

# Stage the bundled templates to a fixed home so /research.init can copy them
# into a paper repo's ./.research/templates/ regardless of where this repo lives.
if [ -d "$SCRIPT_DIR/templates" ]; then
    mkdir -p "$BUNDLE_HOME"
    rm -rf "$BUNDLE_HOME/templates"
    cp -R "$SCRIPT_DIR/templates" "$BUNDLE_HOME/templates"
    echo "  staged   $BUNDLE_HOME/templates (bundled templates for /research.init)"
fi

echo "Done. In your paper repo, run /research.init once, then /research.constitution."
