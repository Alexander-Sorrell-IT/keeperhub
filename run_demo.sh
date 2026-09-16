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
export KEEPERHUB_API_KEY=kh_REDACTED_SEE_DOT_ENV
export THEMIS_POSITION_OWNER=0x9007a515008b4236C8E3644d0A7C8E853B92F4fb
export THEMIS_SAFE_ADDRESS=0x9007a515008b4236C8E3644d0A7C8E853B92F4fb
export PYTHONUNBUFFERED=1

# ── Flags ─────────────────────────────────────────────────────────────────
NO_REC=0
USE_CAM=0
for arg in "$@"; do
    [ "$arg" = "--no-rec"  ] && NO_REC=1
    [ "$arg" = "--cam"     ] && USE_CAM=1
    [ "$arg" = "--debug"   ] && export THEMIS_DEBUG=1
done

# ── Position terminal ──────────────────────────────────────────────────────
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
