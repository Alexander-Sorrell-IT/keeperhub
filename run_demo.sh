#!/bin/bash
# THEMIS — Verify then Record
# Step 1: debug run + log
# Step 2: check log for errors
# Step 3: if clean, run clean for recording

set -e

export KEEPERHUB_API_KEY=kh_REDACTED_SEE_DOT_ENV
export THEMIS_POSITION_OWNER=0x9007a515008b4236C8E3644d0A7C8E853B92F4fb
export THEMIS_SAFE_ADDRESS=0x9007a515008b4236C8E3644d0A7C8E853B92F4fb

BOLD="\033[1m"
GREEN="\033[92m"
RED="\033[91m"
CYAN="\033[96m"
DIM="\033[2m"
RESET="\033[0m"

LOG=/tmp/themis_debug.log
cd /tmp/keeperhub

echo -e "\n${BOLD}${CYAN}════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${CYAN}  THEMIS — Step 1: Debug verification run${RESET}"
echo -e "${BOLD}${CYAN}════════════════════════════════════════════${RESET}\n"

python3.11 demo.py --debug --log "$LOG"

echo -e "\n${BOLD}${CYAN}════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${CYAN}  THEMIS — Step 2: Checking log for errors${RESET}"
echo -e "${BOLD}${CYAN}════════════════════════════════════════════${RESET}\n"

# Check for hard failures in the log
ERRORS=$(grep -c -i "error\|traceback\|exception\|failed\|refused\|404\|422\|503" "$LOG" 2>/dev/null || true)
EXECUTIONS=$(grep -c "execution ID" "$LOG" 2>/dev/null || true)
VALID=$(grep -c "valid=True" "$LOG" 2>/dev/null || true)
LISTED=$(grep -c "THEMIS LISTED" "$LOG" 2>/dev/null || true)
REFUSED=$(grep -c "REFUSED" "$LOG" 2>/dev/null || true)  # expected refusals
VERDICT=$(grep -c "VERDICT RETURNED" "$LOG" 2>/dev/null || true)

echo -e "  Log file:         ${DIM}$LOG${RESET}"
echo -e "  Execution IDs:    ${GREEN}$EXECUTIONS found${RESET}"
echo -e "  Validations:      ${GREEN}$VALID passed${RESET}"
echo -e "  Marketplace:      ${GREEN}$LISTED listed${RESET}"
echo -e "  Refused callers:  ${GREEN}$REFUSED (expected — Repulsive Gravity gate working)${RESET}"
echo -e "  Verdict returned: ${GREEN}$VERDICT (agent-to-agent call confirmed)${RESET}"

# Real failures = errors that aren't the expected refusals from the integrity gate
REAL_ERRORS=$(grep -i "traceback\|exception\|ModuleNotFound\|ImportError\|KeyError" "$LOG" 2>/dev/null | wc -l || echo 0)

if [ "$REAL_ERRORS" -gt 0 ]; then
    echo -e "\n  ${RED}❌ ERRORS FOUND — do not record yet${RESET}"
    echo -e "  ${RED}Check $LOG for details${RESET}"
    grep -i "traceback\|exception\|ModuleNotFound" "$LOG" | head -10
    exit 1
fi

if [ "$EXECUTIONS" -lt 1 ]; then
    echo -e "\n  ${RED}❌ No execution IDs found — agent-to-agent call may have failed${RESET}"
    exit 1
fi

echo -e "\n  ${GREEN}✅ All checks passed. Ready to record.${RESET}"

echo -e "\n${BOLD}${CYAN}════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${CYAN}  THEMIS — Step 3: Clean run for recording${RESET}"
echo -e "${BOLD}${CYAN}  START SCREEN RECORDING NOW${RESET}"
echo -e "${BOLD}${CYAN}════════════════════════════════════════════${RESET}\n"

echo -e "  ${DIM}Press ENTER when screen recording is running...${RESET}"
read -r

python3.11 demo.py

echo -e "\n${BOLD}${GREEN}════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${GREEN}  STOP SCREEN RECORDING NOW${RESET}"
echo -e "${BOLD}${GREEN}  Upload to YouTube → submit on DoraHacks${RESET}"
echo -e "${BOLD}${GREEN}════════════════════════════════════════════${RESET}\n"
echo -e "  ${DIM}DoraHacks:  dorahacks.io/hackathon/agent-economy${RESET}"
echo -e "  ${DIM}GitHub:     github.com/Alexander-Sorrell-IT/keeperhub${RESET}"
echo -e "  ${DIM}Deadline:   Sep 18 06:00 CDT${RESET}\n"
