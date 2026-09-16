#!/bin/bash
# THEMIS — One command. Press ENTER. Demo runs. Video saved to Desktop.
# Mirrors the sentinel run_demo.sh pattern.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLEANREC="/Users/broodierchip-m1air/Desktop/foundersmax-refund-agent/loom/cleanrec/CleanRec.app/Contents/MacOS/CleanRec"
STAMP="$(date +%H%M%S)"
TRIG="/tmp/themis_rec_trigger"
REC_OUT="$HOME/Desktop/themis_demo_${STAMP}.mp4"
LOG="$HOME/Desktop/themis_demo_${STAMP}.log"

# ── Keys ──────────────────────────────────────────────────────────────────
# Secrets live in .env (gitignored), never in this file — it is tracked and the
# repo goes public at submission.
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a; . "$SCRIPT_DIR/.env"; set +a
fi
export THEMIS_POSITION_OWNER="${THEMIS_POSITION_OWNER:-0x9007a515008b4236C8E3644d0A7C8E853B92F4fb}"
export THEMIS_SAFE_ADDRESS="${THEMIS_SAFE_ADDRESS:-0x9007a515008b4236C8E3644d0A7C8E853B92F4fb}"
export PYTHONUNBUFFERED=1

if [ -z "$KEEPERHUB_API_KEY" ]; then
    echo ""
    echo "  KEEPERHUB_API_KEY is not set. Put it in $SCRIPT_DIR/.env as:"
    echo "      KEEPERHUB_API_KEY=kh_..."
    echo ""
    exit 1
fi

# ── Flags ─────────────────────────────────────────────────────────────────
NO_REC=0
USE_CAM=0
NO_TP=0
TP_MANUAL=0
for arg in "$@"; do
    [ "$arg" = "--no-rec"  ] && NO_REC=1
    [ "$arg" = "--cam"     ] && USE_CAM=1
    [ "$arg" = "--debug"   ] && export THEMIS_DEBUG=1
    [ "$arg" = "--no-tp"   ] && NO_TP=1
    [ "$arg" = "--manual"  ] && TP_MANUAL=1
done
TP_ARGS="--trigger $TRIG"
[ "$TP_MANUAL" -eq 1 ] && TP_ARGS="--manual"

# ── Split the screen: demo left half, teleprompter right half ─────────────
# The demo prints into the left window; teleprompter.sh scrolls the spoken
# script in the right one. Both start on the same trigger file, so the
# narration stays in step with what the recording shows.
TP_WIN_ID=""
if [ "$NO_TP" -eq 0 ] && [ -x "$SCRIPT_DIR/teleprompter.sh" ]; then
    TP_WIN_ID=$(osascript <<APPL 2>/dev/null
set screenBounds to {0, 0, 1440, 900}
try
    tell application "Finder" to set screenBounds to bounds of window of desktop
end try
set scrW to item 3 of screenBounds
set scrH to item 4 of screenBounds
set halfW to scrW div 2

tell application "Terminal"
    activate
    -- Left half: this window, where the demo runs.
    try
        set bounds of front window to {0, 25, halfW, scrH}
        set current settings of front window to settings set "Pro"
        set font size of front window to 13
    end try
    -- Right half: a second window running the teleprompter.
    do script "exec bash '$SCRIPT_DIR/teleprompter.sh' $TP_ARGS"
    set tpWin to front window
    try
        set bounds of tpWin to {halfW, 25, scrW, scrH}
        set current settings of tpWin to settings set "Pro"
        set font size of tpWin to 17
    end try
    set tpId to id of tpWin
end tell

-- Hand focus back to the demo window so ENTER lands in the right place.
tell application "Terminal"
    try
        repeat with w in windows
            if id of w is not tpId then
                set frontmost of w to true
                exit repeat
            end if
        end repeat
    end try
end tell
return tpId
APPL
)
else
    osascript <<'APPL' >/dev/null 2>&1
tell application "Terminal"
    activate
    try
        set bounds of front window to {0, 25, 1440, 900}
    end try
    try
        set current settings of front window to settings set "Pro"
        set font size of front window to 15
    end try
end tell
APPL
fi

# ── Arm CleanRec ───────────────────────────────────────────────────────────
rm -f "$TRIG"
REC_PID=""
if [ -x "$CLEANREC" ] && [ "$NO_REC" -eq 0 ]; then
    "$CLEANREC" --fullscreen 1 --cam "$USE_CAM" --trigger "$TRIG" --out "$REC_OUT" >/dev/null 2>&1 &
    REC_PID=$!
fi

# ── Banner ─────────────────────────────────────────────────────────────────
echo ""
echo "  ╔══════════════════════════════════════════════════════════════════╗"
echo "  ║   THEMIS  ·  KeeperHub Agent Economy Hackathon                   ║"
echo "  ╚══════════════════════════════════════════════════════════════════╝"
echo ""
if [ -n "$TP_WIN_ID" ]; then
    echo "  ✓ Teleprompter open on the right half (edit teleprompter.txt to change it)"
fi
if [ -n "$REC_PID" ]; then
    echo "  ✓ Screen recorder armed → ~/Desktop/themis_demo_${STAMP}.mp4"
    echo ""
    printf "  \033[1;92m▸ Press ENTER — recording and demo start together…\033[0m"
else
    printf "  \033[1;93m▸ Press ENTER to begin…\033[0m"
fi
read -r _ || true
echo ""

# ── Start recording ────────────────────────────────────────────────────────
touch "$TRIG" 2>/dev/null || true

# ── Run demo ───────────────────────────────────────────────────────────────
cd "$SCRIPT_DIR"
python3.11 demo.py --log "$LOG"

# ── Hold closing screen for 5s ─────────────────────────────────────────────
sleep 5

# ── Close the teleprompter window ──────────────────────────────────────────
if [ -n "$TP_WIN_ID" ]; then
    osascript -e "tell application \"Terminal\" to close (every window whose id is $TP_WIN_ID)" >/dev/null 2>&1 || true
fi

# ── Stop recording ─────────────────────────────────────────────────────────
if [ -n "$REC_PID" ]; then
    kill -INT "$REC_PID" 2>/dev/null || true
    wait "$REC_PID" 2>/dev/null || true
    echo ""
    echo "  ╔══════════════════════════════════════════════════════════════════╗"
    echo "  ║  ✓ Video saved: ~/Desktop/themis_demo_${STAMP}.mp4              ║"
    echo "  ║  ✓ Log saved:   ~/Desktop/themis_demo_${STAMP}.log              ║"
    echo "  ╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "  Next: upload to YouTube → submit on dorahacks.io/hackathon/agent-economy"
    echo ""
fi
