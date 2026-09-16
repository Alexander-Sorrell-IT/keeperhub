#!/bin/bash
# THEMIS — One screen, split in half. Left = demo. Right = teleprompter.
# Mirrors the sentinel demo_kit pattern: the teleprompter follows a state file
# the demo writes, so the narration advances with real progress, not a timer.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
STATE="/tmp/themis_state"

# ── Load keys ─────────────────────────────────────────────────────────────
# .env is gitignored. Nothing secret belongs in this file — it is tracked.
if [ -f "$ENV_FILE" ]; then
    set -o allexport
    source "$ENV_FILE"
    set +o allexport
fi

: "${KEEPERHUB_API_KEY:?Missing — add KEEPERHUB_API_KEY to .env}"

export THEMIS_POSITION_OWNER="${THEMIS_POSITION_OWNER:-0x9007a515008b4236C8E3644d0A7C8E853B92F4fb}"
export THEMIS_SAFE_ADDRESS="${THEMIS_SAFE_ADDRESS:-$THEMIS_POSITION_OWNER}"
export PYTHONUNBUFFERED=1

# ── Reset state file ───────────────────────────────────────────────────────
echo "0" > "$STATE"

# ── Flags ─────────────────────────────────────────────────────────────────
USE_CAM=0
NO_REC=0
NO_TP=0
PASS_ARGS=()
for arg in "$@"; do
    case "$arg" in
        --debug)  export THEMIS_DEBUG=1; PASS_ARGS+=("--debug") ;;
        --cam)    USE_CAM=1 ;;
        --no-rec) NO_REC=1 ;;
        --no-tp)  NO_TP=1 ;;
        *)        PASS_ARGS+=("$arg") ;;
    esac
done

# ── Ensure Terminal is not in macOS native fullscreen ──────────────────────
osascript <<'EOF' >/dev/null 2>&1
tell application "System Events"
    tell process "Terminal"
        try
            if value of attribute "AXFullScreen" of front window then
                set value of attribute "AXFullScreen" of front window to false
                delay 0.8
            end if
        end try
    end tell
end tell
EOF

# ── Get screen dimensions ──────────────────────────────────────────────────
SCREEN_INFO=$(swift -e '
import Cocoa
if let s = NSScreen.main {
    let f = s.frame
    let v = s.visibleFrame
    let menuH = max(25, Int(f.height - (v.origin.y + v.height)))
    print("\(Int(f.width)) \(Int(f.height)) \(Int(v.width / 2)) \(menuH)")
} else {
    print("1440 900 720 25")
}
')
read -r SCREEN_W SCREEN_H HALF_W MENU_H <<< "$SCREEN_INFO"

# ── Position THIS terminal window on the LEFT half ────────────────────────
osascript <<EOF >/dev/null 2>&1
tell application "Terminal"
    activate
    set bounds of front window to {0, $MENU_H, $HALF_W, $SCREEN_H}
    try
        set current settings of front window to settings set "Pro"
    end try
    set font size of front window to 14
end tell
EOF

# ── Auto-recorder (CleanRec) setup ─────────────────────────────────────────
CLEANREC="/Users/broodierchip-m1air/Desktop/foundersmax-refund-agent/loom/cleanrec/CleanRec.app/Contents/MacOS/CleanRec"
STAMP="$(date +%H%M%S)"
TRIG="/tmp/themis_rec_trigger"
REC_OUT="$HOME/Desktop/themis_demo_${STAMP}.mp4"
LOG="$HOME/Desktop/themis_demo_${STAMP}.log"
rm -f "$TRIG"

REC_PID=""
if [ -x "$CLEANREC" ] && [ "$NO_REC" -eq 0 ]; then
    "$CLEANREC" --fullscreen 1 --cam "$USE_CAM" --trigger "$TRIG" --out "$REC_OUT" >/dev/null 2>&1 &
    REC_PID=$!
fi

# ── Kill any stale teleprompter instances ──────────────────────────────────
pkill -f "$SCRIPT_DIR/teleprompter" 2>/dev/null || true

# ── Build the teleprompter if it is missing or out of date ─────────────────
# The binary is gitignored; anyone cloning gets it built on first run.
if [ "$NO_TP" -eq 0 ] && [ -f "$SCRIPT_DIR/teleprompter.swift" ]; then
    if [ ! -x "$SCRIPT_DIR/teleprompter" ] || \
       [ "$SCRIPT_DIR/teleprompter.swift" -nt "$SCRIPT_DIR/teleprompter" ]; then
        echo "  Building teleprompter…"
        swiftc -O -o "$SCRIPT_DIR/teleprompter" "$SCRIPT_DIR/teleprompter.swift" \
            2>/tmp/themis_teleprompter_build.log \
            || echo "  (teleprompter build failed — see /tmp/themis_teleprompter_build.log)"
    fi
fi

# ── Launch Swift teleprompter (positions itself on the RIGHT half) ─────────
TP_PID=""
if [ -x "$SCRIPT_DIR/teleprompter" ] && [ "$NO_TP" -eq 0 ]; then
    "$SCRIPT_DIR/teleprompter" "$STATE" 2>/tmp/themis_teleprompter.log &
    TP_PID=$!
    sleep 0.5
fi

# ── Keep focus on Terminal ─────────────────────────────────────────────────
osascript -e 'tell application "Terminal" to activate' >/dev/null 2>&1

# ── Clean banner hold — ENTER starts all 3 (Demo + Prompter + Recording) ───
echo ""
echo "  ╔══════════════════════════════════════════════════════════════════╗"
echo "  ║   THEMIS  ·  KeeperHub Agent Economy Hackathon                   ║"
echo "  ╚══════════════════════════════════════════════════════════════════╝"
echo ""
if [ -n "$TP_PID" ]; then
    echo "  ✓ Windows locked 50/50 (Terminal left, Teleprompter right)"
fi
if [ -n "$REC_PID" ]; then
    echo "  ✓ Screen recorder armed -> ~/Desktop/themis_demo_${STAMP}.mp4"
    echo ""
    printf "  \033[1;92m▸ Press ENTER — recording, teleprompter, and demo start together…\033[0m"
else
    echo ""
    printf "  \033[1;93m▸ Press ENTER to begin…\033[0m"
fi
read -r _ || true
echo ""
touch "$TRIG" 2>/dev/null || true

# ── Run demo ───────────────────────────────────────────────────────────────
cd "$SCRIPT_DIR"
python3.11 demo.py --log "$LOG" "${PASS_ARGS[@]}"

# ── Hold closing screen for video capture ──────────────────────────────────
sleep 5

# ── Stop recording and finalize MP4 ────────────────────────────────────────
if [ -n "$REC_PID" ]; then
    kill -INT "$REC_PID" 2>/dev/null || true
    wait "$REC_PID" 2>/dev/null || true
    REC_PID=""
    echo ""
    echo "  ╔══════════════════════════════════════════════════════════════════╗"
    echo "  ║  ✓ Video saved: ~/Desktop/themis_demo_${STAMP}.mp4"
    echo "  ║  ✓ Log saved:   ~/Desktop/themis_demo_${STAMP}.log"
    echo "  ╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "  Next: upload to YouTube → submit on dorahacks.io/hackathon/agent-economy"
    echo ""
fi

# ── Clean up teleprompter ──────────────────────────────────────────────────
[ -n "$TP_PID" ] && kill "$TP_PID" 2>/dev/null || true
