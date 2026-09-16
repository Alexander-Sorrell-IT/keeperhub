#!/bin/bash
# THEMIS teleprompter — right half of the screen while demo.py runs on the left.
#
#   teleprompter.sh [--manual] [--trigger FILE] [--script FILE]
#
# Default: waits for the trigger file that run_demo.sh touches when you press
# ENTER, then auto-advances each beat on its own dwell (the "## <seconds>"
# header in teleprompter.txt). --manual advances on ENTER instead.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$SCRIPT_DIR/teleprompter.txt"
TRIG=""
MANUAL=0

while [ $# -gt 0 ]; do
    case "$1" in
        --manual)  MANUAL=1 ;;
        --trigger) TRIG="$2"; shift ;;
        --script)  SCRIPT="$2"; shift ;;
    esac
    shift
done

BOLD=$'\033[1m'; DIM=$'\033[2m'; GREEN=$'\033[92m'; CYAN=$'\033[96m'; RESET=$'\033[0m'

[ -f "$SCRIPT" ] || { echo "teleprompter: no script at $SCRIPT"; sleep 5; exit 1; }

# ── Parse beats: "## n" starts a beat with dwell n; blank line ends it ──────
beats=(); dwells=(); cur=""; dwell=18
flush() {
    # Drop leading blank lines, and skip beats that are only whitespace.
    while [ "${cur:0:1}" = $'\n' ]; do cur="${cur:1}"; done
    if [ -n "${cur//[$'\n\t ']/}" ]; then
        beats+=("$cur"); dwells+=("$dwell")
    fi
    cur=""
}
while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
        '## '*) flush; dwell="${line#\#\# }" ;;
        '#'*)   ;;
        '')     cur="$cur"$'\n' ;;
        *)      cur="$cur$line"$'\n' ;;
    esac
done < "$SCRIPT"
flush

total=${#beats[@]}
[ "$total" -eq 0 ] && { echo "teleprompter: $SCRIPT has no beats"; sleep 5; exit 1; }

clear
echo ""
echo "  ${BOLD}${CYAN}THEMIS teleprompter${RESET}   ${DIM}${total} beats${RESET}"
echo ""
if [ "$MANUAL" -eq 1 ]; then
    echo "  ${DIM}ENTER advances. Ctrl-C quits.${RESET}"
else
    echo "  ${DIM}Auto-advance. Waiting for the demo to start…${RESET}"
    # Wait for run_demo.sh to touch the trigger, so both halves start together.
    if [ -n "$TRIG" ]; then
        while [ ! -f "$TRIG" ]; do sleep 0.1; done
    fi
fi

i=0
for beat in "${beats[@]}"; do
    i=$((i + 1))
    clear
    echo ""
    echo "  ${DIM}${i}/${total}${RESET}"
    echo ""
    # Indent and brighten the body; the first line of each beat is its cue.
    first=1
    while IFS= read -r l; do
        if [ "$first" -eq 1 ] && [ -n "$l" ]; then
            echo "  ${BOLD}${GREEN}${l}${RESET}"
            echo ""
            first=0
        else
            echo "  ${BOLD}${l}${RESET}"
        fi
    done <<< "$beat"
    if [ "$MANUAL" -eq 1 ]; then
        read -r _ || break
    else
        sleep "${dwells[$((i - 1))]}"
    fi
done

clear
echo ""
echo "  ${DIM}— end of script —${RESET}"
echo ""
sleep 30
