#!/bin/bash
# Link PARA payloads to this permanent checkout. Bash 3 compatible; requires jq/Git.
# Shared containers and active global AGENTS.md are preserved. One operator per root.
set -euo pipefail

DRY_RUN=0
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
        -h|--help) echo "Usage: $0 [--dry-run]"; exit 0 ;;
        *) echo "Error: unknown argument: $arg" >&2; exit 1 ;;
    esac
done
fail() { echo "Error: $*" >&2; exit 1; }
for dependency in jq git dirname cat readlink stat cksum mkdir mktemp mv cp ln rm date; do
    command -v "$dependency" >/dev/null 2>&1 || fail "Required dependency missing: $dependency"
done

SOURCE=$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
# Resolve existing directory ancestors without creating anything. Leaf entries are
# deliberately NOT passed here: their symlink targets are not write locations.
physical_dir() {
    local path="$1" parent name
    case "$path" in /*) ;; *) path="$PWD/$path" ;; esac
    if [ -d "$path" ]; then (cd -P "$path" && pwd -P); return; fi
    if [ -e "$path" ] || [ -L "$path" ]; then
        echo "Error: not a directory container: $path" >&2; return 1
    fi
    path=${path%/}; name=${path##*/}; parent=${path%/*}
    parent=$(physical_dir "${parent:-/}") || return 1
    case "$name" in
        .) printf '%s\n' "$parent" ;;
        ..) dirname "$parent" ;;
        *) printf '%s/%s\n' "${parent%/}" "$name" ;;
    esac
}
within() { [ "$1" = "$2" ] || [[ "$1" == "${2%/}/"* ]]; }
check_container_path() {
    within "$1" "$SOURCE" && fail "Container is inside source checkout: $1"
    return 0
}
check_write_path() {
    within "$1" "$SOURCE" && fail "Destination is inside source checkout: $1"
    within "$SOURCE" "$1" && fail "Destination would replace an ancestor of source: $1"
    return 0
}
kind() {
    if [ -L "$1" ]; then echo link
    elif [ -d "$1" ]; then echo directory
    elif [ -f "$1" ]; then echo file
    elif [ -e "$1" ]; then fail "Unsupported destination entry: $1"
    else echo absent; fi
}
# Capture identity and regular-file content. This detects changes between preflight
# and publication, not adversarial filesystem races (one installer is assumed).
if stat -f '%d:%i:%m:%z' "$SOURCE" >/dev/null 2>&1; then STAT_STYLE=bsd; else STAT_STYLE=gnu; fi
identity() {
    local type
    type=$(kind "$1")
    printf '%s:' "$type"
    [ "$type" != absent ] || return 0
    if [ "$STAT_STYLE" = bsd ]; then stat -f '%d:%i:%m:%z' "$1"; else stat -c '%d:%i:%Y:%s' "$1"; fi
    case "$type" in
        link) readlink "$1" ;;
        file) cksum < "$1" ;;
    esac
}
classify_entry() {
    local target parent
    if [ -L "$2" ]; then
        target=$(readlink "$2")
        case "$target" in /*) ;; *) target="${2%/*}/$target" ;; esac
        # Accept equivalent relative links too; a broken link remains a collision.
        if [ -e "$target" ]; then
            parent=$(physical_dir "${target%/*}") || return 1
            if [ "$parent/${target##*/}" = "$1" ]; then echo unchanged; return; fi
            if [ -d "$target" ] && [ "$(physical_dir "$target")" = "$1" ]; then echo unchanged; return; fi
        fi
    fi
    if [ -e "$2" ] || [ -L "$2" ]; then echo backup-and-link; else echo link; fi
}

# Reject linked execution worktrees: archived worktrees cannot own live installs.
[ "$(git -C "$SOURCE" rev-parse --show-toplevel 2>/dev/null)" = "$SOURCE" ] || fail "Run from a permanent primary Git checkout"
git_dir=$(cd "$SOURCE" && cd "$(git rev-parse --git-dir)" && pwd -P)
common_dir=$(cd "$SOURCE" && cd "$(git rev-parse --git-common-dir)" && pwd -P)
[ "$git_dir" = "$common_dir" ] || fail "Linked worktree source rejected. Run the merged installer from the permanent primary checkout."
[ -d "$SOURCE/skills" ] && [ -f "$SOURCE/docs/METHODOLOGY.md" ] && [ -f "$SOURCE/resources/AGENTS.md" ] || fail "Incomplete skills/docs/resources payload: $SOURCE"

ROOTS=()
for root in "${AGENTS_HOME:-$HOME/.agents}" "${CODEX_HOME:-$HOME/.codex}"; do
    root=$(physical_dir "$root")
    check_container_path "$root"
    duplicate=0
    for prior in "${ROOTS[@]+"${ROOTS[@]}"}"; do
        if [ "$root" = "$prior" ]; then duplicate=1
        elif within "$root" "$prior" || within "$prior" "$root"; then fail "Overlapping install roots: $root and $prior"; fi
    done
    [ "$duplicate" -eq 1 ] || ROOTS[${#ROOTS[@]}]="$root"
done
SOURCES=(); DESTS=(); OWNERS=(); ACTIONS=(); IDENTITIES=(); STATES=()
CONTAINERS=(); BACKUP_BASES=(); RUN_DIRS=()
add_entry() {
    local source="$1" destination="$2" owner="$3" i
    check_write_path "$destination"
    for ((i=0; i<${#DESTS[@]}; i++)); do
        if [ "$destination" = "${DESTS[$i]}" ]; then
            [ "$source" = "${SOURCES[$i]}" ] || fail "Conflicting destination: $destination"
            return
        fi
        if within "$destination" "${DESTS[$i]}" || within "${DESTS[$i]}" "$destination"; then fail "Overlapping payload destinations: $destination"; fi
    done
    i=${#DESTS[@]}
    SOURCES[i]="$source"; DESTS[i]="$destination"; OWNERS[i]="$owner"
    ACTIONS[i]=$(classify_entry "$source" "$destination")
    IDENTITIES[i]=$(identity "$destination"); STATES[i]=pending
}
shopt -s nullglob dotglob
for ((r=0; r<${#ROOTS[@]}; r++)); do
    root=${ROOTS[$r]}
    for container in skills docs resources; do
        path=$(physical_dir "$root/$container")
        check_container_path "$path"
        CONTAINERS[${#CONTAINERS[@]}]="$path"
        case "$container" in
            skills)
                skill_count=0
                for source in "$SOURCE"/skills/para-*; do
                    [ -d "$source" ] && [ -f "$source/SKILL.md" ] || fail "Invalid skill payload: $source"
                    add_entry "$source" "$path/${source##*/}" "$r"
                    skill_count=$((skill_count+1))
                done
                [ "$skill_count" -gt 0 ] || fail "Empty skill payload" ;;
            docs)
                for source in "$SOURCE"/docs/*; do add_entry "$source" "$path/${source##*/}" "$r"; done ;;
            resources) add_entry "$SOURCE/resources/AGENTS.md" "$path/AGENTS.md" "$r" ;;
        esac
    done
    BACKUP_BASES[r]=$(physical_dir "$root/para-install-backups")
    RUN_DIRS[r]=''
done
REGISTRY_PARENT=$(physical_dir "${ROOTS[0]}/plugins")
REGISTRY="$REGISTRY_PARENT/marketplace.json"
check_container_path "$REGISTRY_PARENT"
check_write_path "$REGISTRY"
for destination in "${DESTS[@]}"; do
    if within "$REGISTRY" "$destination" || within "$destination" "$REGISTRY"; then fail "Registry overlaps payload: $destination"; fi
done
for backup in "${BACKUP_BASES[@]}"; do
    check_write_path "$backup"
    for path in "${CONTAINERS[@]}" "$REGISTRY_PARENT"; do
        if within "$backup" "$path" || within "$path" "$backup"; then fail "Backup location overlaps payload/registry container: $backup"; fi
    done
done
# Existing registry validation occurs before any mkdir/move/link operation.
REGISTRY_ID=$(identity "$REGISTRY")
if [ -e "$REGISTRY" ] || [ -L "$REGISTRY" ]; then
    [ -f "$REGISTRY" ] || fail "Registry is not a readable JSON file: $REGISTRY"
    OLD_JSON=$(cat "$REGISTRY")
else
    OLD_JSON='{"name":"personal-plugins","interface":{"displayName":"Personal Plugins"},"plugins":[]}'
fi
printf '%s\n' "$OLD_JSON" | jq -es '
    length == 1 and (.[0] |
    type == "object" and (.plugins | type == "array") and
    all(.plugins[]; type == "object") and
    ([.plugins[] | select(.name == "para-programming")] | length <= 1) and
    all(.plugins[] | select(.name == "para-programming");
        .source.source == "local" and (.source.path | type == "string") and (.source.path | length > 0)))
' >/dev/null || fail "Malformed, ambiguous or nonlocal PARA registry: $REGISTRY"
NEW_JSON=$(printf '%s\n' "$OLD_JSON" | jq --arg path "$SOURCE" '
    if any(.plugins[]; .name == "para-programming") then
        (.plugins[] | select(.name == "para-programming") | .source.path) = $path
    else .plugins += [{name:"para-programming",source:{source:"local",path:$path},
        policy:{installation:"AVAILABLE",authentication:"ON_INSTALL"},category:"Productivity"}] end')
REGISTRY_CHANGE=1
if [ -f "$REGISTRY" ] && [ "$(printf '%s' "$OLD_JSON" | jq -cS .)" = "$(printf '%s' "$NEW_JSON" | jq -cS .)" ]; then REGISTRY_CHANGE=0; fi

printf 'PARA source: %s\n' "$SOURCE"
for ((i=0; i<${#DESTS[@]}; i++)); do printf '%s: %s -> %s\n' "${ACTIONS[$i]}" "${DESTS[$i]}" "${SOURCES[$i]}"; done
for root in "${ROOTS[@]}"; do
    for stale in "$root"/skills/para-* "$root"/docs/*; do
        [ -L "$stale" ] && [ ! -e "$stale" ] || continue
        target=$(readlink "$stale")
        case "$target" in "$SOURCE/skills/"*|"$SOURCE/docs/"*) printf 'Stale link (inspect and remove manually): %s -> %s\n' "$stale" "$target" ;; esac
    done
done
printf 'Registry update=%s: %s\n' "$REGISTRY_CHANGE" "$REGISTRY"
if [ "$DRY_RUN" -eq 1 ]; then
    for backup in "${BACKUP_BASES[@]}"; do printf 'Collisions will be preserved under: %s/<unique-run-id>/\n' "$backup"; done
    echo 'Dry run: no filesystem changes made'; exit 0
fi

created=0; unchanged=0; backed_up=0; ACTIVE_DEST=''; ACTIVE_BACKUP=''; STAGE_DIR=''; REGISTRY_STATE=pending
ensure_run_dir() {
    local owner="$1"
    if [ -z "${RUN_DIRS[$owner]}" ]; then
        mkdir -p "${BACKUP_BASES[$owner]}"
        RUN_DIRS[owner]=$(mktemp -d "${BACKUP_BASES[$owner]}/$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
        printf 'Recovery manifest: %s/manifest.jsonl\n' "${RUN_DIRS[$owner]}"
    fi
}
record() {
    local owner="$1" event="$2" source="$3" destination="$4" backup="$5" original="$6"
    jq -nc --arg event "$event" --arg source "$source" --arg destination "$destination" \
        --arg backup "$backup" --arg original_kind "$original" \
        '{event:$event,source:$source,destination:$destination,backup:$backup,original_kind:$original_kind}' >> "${RUN_DIRS[$owner]}/manifest.jsonl"
}
# The manifest precedes the move; even SIGKILL after the move leaves a recovery map.
reserve_backup() {
    local owner="$1" destination="$2" relative
    ensure_run_dir "$owner"
    # Destination containers may themselves be links. Use the inventory's logical
    # role for the backup path so external container paths cannot escape the run dir.
    case "$destination" in
        "$REGISTRY") relative=plugins/marketplace.json ;;
        *) relative="$BACKUP_RELATIVE" ;;
    esac
    ACTIVE_BACKUP="${RUN_DIRS[$owner]}/$relative"
    [ ! -e "$ACTIVE_BACKUP" ] && [ ! -L "$ACTIVE_BACKUP" ] || fail "Backup already exists: $ACTIVE_BACKUP"
    mkdir -p "${ACTIVE_BACKUP%/*}"
}
cleanup() {
    local rc=$? i
    trap - EXIT HUP INT TERM
    set +e
    if [ "$rc" -ne 0 ]; then
        if [ -n "$ACTIVE_BACKUP" ] && { [ -e "$ACTIVE_BACKUP" ] || [ -L "$ACTIVE_BACKUP" ]; } &&
           [ ! -e "$ACTIVE_DEST" ] && [ ! -L "$ACTIVE_DEST" ]; then
            mv "$ACTIVE_BACKUP" "$ACTIVE_DEST" && printf 'Restored: %s\n' "$ACTIVE_DEST" >&2
        fi
        printf 'Installation incomplete (exit %s). Failed/current: %s\n' "$rc" "$ACTIVE_DEST" >&2
        for ((i=0; i<${#DESTS[@]}; i++)); do printf '%s: %s\n' "${STATES[$i]}" "${DESTS[$i]}" >&2; done
        printf 'Registry %s: %s\n' "$REGISTRY_STATE" "$REGISTRY" >&2
        for path in "${RUN_DIRS[@]}"; do
            [ -z "$path" ] || printf 'Recovery: inspect %s/manifest.jsonl and backups; restore only after verifying the destination leaf. Rerun to finish pending entries.\n' "$path" >&2
        done
    fi
    [ -z "$STAGE_DIR" ] || rm -rf "$STAGE_DIR"
    exit "$rc"
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
for ((i=0; i<${#DESTS[@]}; i++)); do
    destination=${DESTS[$i]}; source=${SOURCES[$i]}; owner=${OWNERS[$i]}
    ACTIVE_DEST="$destination"; ACTIVE_BACKUP=''
    [ "$(identity "$destination")" = "${IDENTITIES[$i]}" ] || fail "Destination changed since preflight: $destination"
    if [ "${ACTIONS[$i]}" = unchanged ]; then
        STATES[i]=unchanged; unchanged=$((unchanged+1)); continue
    fi
    [ "$(physical_dir "${destination%/*}")" = "${destination%/*}" ] || fail "Destination parent changed: $destination"
    mkdir -p "${destination%/*}"
    STAGE_DIR=$(mktemp -d "${destination%/*}/.para-link-XXXXXX")
    ln -s "$source" "$STAGE_DIR/entry"
    [ "$(identity "$destination")" = "${IDENTITIES[$i]}" ] || fail "Destination changed before publication: $destination"
    if [ "${ACTIONS[$i]}" = backup-and-link ]; then
        BACKUP_RELATIVE=${source#"$SOURCE/"}
        reserve_backup "$owner" "$destination"
        original=$(kind "$destination")
        record "$owner" intent "$source" "$destination" "$ACTIVE_BACKUP" "$original"
        mv "$destination" "$ACTIVE_BACKUP"
        record "$owner" backed-up "$source" "$destination" "$ACTIVE_BACKUP" "$original"
        backed_up=$((backed_up+1))
    fi
    [ ! -e "$destination" ] && [ ! -L "$destination" ] || fail "Destination appeared during install: $destination"
    mv "$STAGE_DIR/entry" "$destination"
    STATES[i]=completed; created=$((created+1))
    if [ -n "$ACTIVE_BACKUP" ]; then record "$owner" completed "$source" "$destination" "$ACTIVE_BACKUP" "$original"; fi
    ACTIVE_BACKUP=''; rm -rf "$STAGE_DIR"; STAGE_DIR=''
done
ACTIVE_DEST="$REGISTRY"; ACTIVE_BACKUP=''
[ "$(identity "$REGISTRY")" = "$REGISTRY_ID" ] || fail "Registry changed since preflight: $REGISTRY"
if [ "$REGISTRY_CHANGE" -eq 1 ]; then
    mkdir -p "$REGISTRY_PARENT"
    STAGE_DIR=$(mktemp -d "$REGISTRY_PARENT/.para-registry-XXXXXX")
    printf '%s\n' "$NEW_JSON" > "$STAGE_DIR/entry"
    if [ -e "$REGISTRY" ] || [ -L "$REGISTRY" ]; then
        reserve_backup 0 "$REGISTRY"
        original=$(kind "$REGISTRY")
        record 0 intent "$SOURCE" "$REGISTRY" "$ACTIVE_BACKUP" "$original"
        # Preserve the old registry at its leaf until atomic publication succeeds.
        # Copy the symlink object itself, never write through it to the target.
        if [ -L "$REGISTRY" ]; then ln -s "$(readlink "$REGISTRY")" "$ACTIVE_BACKUP"
        else cp -p "$REGISTRY" "$ACTIVE_BACKUP"; fi
        record 0 backed-up "$SOURCE" "$REGISTRY" "$ACTIVE_BACKUP" "$original"
        backed_up=$((backed_up+1))
    fi
    mv -f "$STAGE_DIR/entry" "$REGISTRY"
    if [ -n "$ACTIVE_BACKUP" ]; then record 0 completed "$SOURCE" "$REGISTRY" "$ACTIVE_BACKUP" "$original"; fi
    ACTIVE_BACKUP=''; rm -rf "$STAGE_DIR"; STAGE_DIR=''
fi
REGISTRY_STATE=completed
printf 'Done: created=%s unchanged=%s backed-up=%s\n' "$created" "$unchanged" "$backed_up"
echo 'Restart or reload your client to discover the linked skills.'
echo 'Use the para-init skill to initialize PARA in a project.'
echo 'Use /skills to browse installed skills.'
