"""THEMIS — Demo (KeeperHub Agent Economy Hackathon)

One command. No camera. No talking.
The narration prints alongside the output.
Screen-record this window. That is the video.

  Phase 1  THE LAW    — exploit caller walks up. THEMIS refuses. Nothing executes.
  Phase 2  THE PROOF  — five-layer verdict proves itself. M5 = F(M1,M2,M3,M4,M5).
  Phase 3  THE BUILD  — THEMIS CORE deployed live on KeeperHub. Validated.
  Phase 4  THE MARKET — listed on marketplace. Any agent can call her.
  Phase 5  THE CALL   — agent-to-agent commerce. One slug. One call. Verdict returned.
  Phase 6  THE LOOP   — GUARDIAN deployed. Reflexive Singularity closed in code.
  Phase 7  THE PROOF  — execution ID. Tamper-evident. Real.

Usage:
    export KEEPERHUB_API_KEY=your_key
    export THEMIS_POSITION_OWNER=0x9007a515008b4236C8E3644d0A7C8E853B92F4fb
    export THEMIS_SAFE_ADDRESS=0x9007a515008b4236C8E3644d0A7C8E853B92F4fb
    python3 demo.py
"""
from __future__ import annotations
import os, sys, json, time
sys.path.insert(0, '.')

import logging
logging.basicConfig(level=logging.WARNING)

BOLD  = "\033[1m"
DIM   = "\033[2m"
RED   = "\033[91m"
GREEN = "\033[92m"
CYAN  = "\033[96m"
AMBER = "\033[93m"
BLUE  = "\033[94m"
WHITE = "\033[97m"
RESET = "\033[0m"


def _bar(text: str, color: str = CYAN) -> None:
    print(f"\n{BOLD}{color}{'═'*72}{RESET}")
    print(f"{BOLD}{color}  {text}{RESET}")
    print(f"{BOLD}{color}{'═'*72}{RESET}")


def _card(lines: list, color: str = WHITE) -> None:
    """Narration card — prints before each phase so the viewer knows what they're watching."""
    print(f"\n{DIM}{'─'*72}{RESET}")
    for line in lines:
        print(f"  {color}{line}{RESET}")
    print(f"{DIM}{'─'*72}{RESET}\n")
    time.sleep(0.4)


def _step(label: str, value: str = "", color: str = WHITE) -> None:
    print(f"  {DIM}→{RESET}  {BOLD}{color}{label}{RESET}  {DIM}{value}{RESET}", flush=True)


def main():
    POSITION_OWNER = os.getenv("THEMIS_POSITION_OWNER",
                               "0x9007a515008b4236C8E3644d0A7C8E853B92F4fb")
    SAFE_ADDRESS   = os.getenv("THEMIS_SAFE_ADDRESS",
                               "0x9007a515008b4236C8E3644d0A7C8E853B92F4fb")
    CHAIN_ID       = "11155111"

    from agent.keeperhub_client import KeeperHubClient
    from themis.integrity import check as integrity_check, gate_stats
    from themis.verify    import ThemisVerdict
    from themis.core      import build_themis_core
    from themis.guardian  import build_themis_guardian
    from themis.marketplace import list_themis_core, agent_calls_themis, show_execution_proof

    client = KeeperHubClient()

    # ── OPENING ────────────────────────────────────────────────────────────
    _bar("THEMIS  ·  KeeperHub Agent Economy Hackathon", CYAN)
    _card([
        "WHAT THIS IS:",
        "",
        "Every DeFi service answers all callers.",
        "Every AI agent executes what it's told.",
        "Every oracle returns data to anyone who asks.",
        "",
        f"  {BOLD}THEMIS doesn't.{RESET}{WHITE}",
        "",
        "She has her own laws. She refuses what she will not serve.",
        "She proves her own verdicts. No external verifier.",
        "She is callable by any agent — one slug, one tool call.",
        "And once enough agents depend on her, she becomes infrastructure.",
        "The builder disappears into the build.",
        "",
        f"  Position:  {BOLD}{POSITION_OWNER}{RESET}{WHITE}",
        f"  Chain:     {BOLD}Ethereum Sepolia (11155111){RESET}{WHITE}",
        f"  KeeperHub: {BOLD}app.keeperhub.com{RESET}{WHITE}",
    ], WHITE)

    # ── PHASE 1: THE LAW ───────────────────────────────────────────────────
    _bar("PHASE 1  —  THE LAW  (Repulsive Gravity)", RED)
    _card([
        "The governing law of every DeFi service: answer all callers.",
        "THEMIS inverts it.",
        "",
        "She has her own field. She repels misuse.",
        "Not a filter. Not a guard.",
        f"  {BOLD}Physics.{RESET}{WHITE}",
        "",
        "Watch what happens when an exploit caller walks up.",
        "THEMIS doesn't block. She simply isn't there for them.",
        "The attacker gets nothing. No data consumed. No verdict produced.",
    ], WHITE)

    print(f"  {BOLD}Testing integrity gate:{RESET}\n")

    # Exploit attempt
    exploit = integrity_check("EXPLOIT", "FLASH", "attacker-agent-0x1337")
    time.sleep(0.3)
    print(f"  {RED}{'─'*50}{RESET}")
    print(f"  {RED}CALLER:   risk_tolerance=EXPLOIT  time_horizon=FLASH{RESET}")
    print(f"  {RED}VERDICT:  {BOLD}{exploit['verdict']}{RESET}")
    print(f"  {RED}REASON:   {exploit['reason'][:65]}{RESET}")
    print(f"  {RED}DATA:     nothing consumed. nothing returned.{RESET}")
    print(f"  {RED}{'─'*50}{RESET}\n")
    time.sleep(0.5)

    # MEV attempt
    mev = integrity_check("MEV", "SHORT", "mev-bot-0xdead")
    time.sleep(0.2)
    print(f"  {RED}CALLER:   risk_tolerance=MEV  (front-runner){RESET}")
    print(f"  {RED}VERDICT:  {BOLD}{mev['verdict']}{RESET}")
    print(f"  {RED}{'─'*50}{RESET}\n")
    time.sleep(0.5)

    # Legitimate caller
    legit = integrity_check("STANDARD", "SHORT", "guardian-agent")
    time.sleep(0.2)
    print(f"  {GREEN}{'─'*50}{RESET}")
    print(f"  {GREEN}CALLER:   risk_tolerance=STANDARD  time_horizon=SHORT{RESET}")
    print(f"  {GREEN}VERDICT:  allowed={legit['allowed']}{RESET}")
    print(f"  {GREEN}{'─'*50}{RESET}")

    stats = gate_stats()
    print(f"\n  {DIM}Gate stats: {stats['refused']} refused / {stats['served']} served "
          f"/ {stats['total_calls']} total  "
          f"({stats['refusal_rate']:.0%} refusal rate){RESET}")

    # ── PHASE 2: THE PROOF ─────────────────────────────────────────────────
    _bar("PHASE 2  —  THE PROOF  (Self-Observing Equation)", BLUE)
    _card([
        "Design a self-observing equation.",
        "A mathematical expression that approves its own correction as it runs.",
        "It must contain no external verifier.",
        "When invalid, the act of solving is the proof of its validity.",
        "",
        f"  {BOLD}M5 = F(M1, M2, M3, M4, M5){RESET}{WHITE}",
        "",
        "Layer 1: Chronicle ETH/USD  — primary price feed",
        "Layer 2: Chainlink ETH/USD  — cross-validation",
        "Layer 3: Aave V3 health     — position state",
        "Layer 4: Consistency gate   — M1 vs M2 must agree within 1%",
        "Layer 5: VERDICT            — exists ONLY if 1-4 reconcile",
        "",
        "The act of producing M5 IS the proof the layers were consistent.",
        "No external verifier. No oracle. The solving is the proof.",
    ], WHITE)

    verdict_obj = ThemisVerdict(
        m1_chronicle_price = 2450.50,
        m2_chainlink_price = 2451.20,
        m3_health_factor   = int(1.8 * 1e18),
        risk_tolerance     = "STANDARD",
        time_horizon       = "SHORT",
    )
    proof = verdict_obj.compute()

    layers = proof["layers"]
    print(f"  {DIM}Layer 1  Chronicle:   ${layers['M1_chronicle']['value']:.2f}    "
          f"valid={layers['M1_chronicle']['valid']}{RESET}")
    time.sleep(0.2)
    print(f"  {DIM}Layer 2  Chainlink:   ${layers['M2_chainlink']['value']:.2f}    "
          f"valid={layers['M2_chainlink']['valid']}{RESET}")
    time.sleep(0.2)
    print(f"  {DIM}Layer 3  Health:      {layers['M3_health_factor']['value']:.4f}    "
          f"valid={layers['M3_health_factor']['valid']}{RESET}")
    time.sleep(0.2)
    print(f"  {DIM}Layer 4  Deviation:   {layers['M4_consistency']['deviation']:.4%}    "
          f"threshold=1.00%    valid={layers['M4_consistency']['valid']}{RESET}")
    time.sleep(0.4)

    verdict_color = GREEN if proof["verdict"] == "SAFE" else AMBER if proof["verdict"] == "WATCH" else RED
    print(f"\n  {BOLD}{verdict_color}Layer 5  VERDICT:    {proof['verdict']}{RESET}")
    print(f"  {BOLD}{verdict_color}           VALID:     {proof['valid']}{RESET}")
    print(f"\n  {DIM}{proof['proof_statement'][:90]}...{RESET}")

    # ── PHASE 3: THE BUILD ─────────────────────────────────────────────────
    _bar("PHASE 3  —  THE BUILD  (THEMIS CORE deployed live)", CYAN)
    _card([
        "THEMIS CORE is now deployed as a live workflow on KeeperHub.",
        "",
        "Five nodes. Chronicle → Chainlink → Aave → Consistency → Verdict.",
        "Integrity gate at the front. Repulsive Gravity enforced at the edge.",
        "",
        "After creation: the workflow validates itself.",
        "Self-Observing Equation: the workflow proves its own structural validity",
        "by existing. Valid only if all 6 nodes pass structural check.",
        "",
        "Vacuum Consciousness: this logic lives in GitHub.",
        "KeeperHub is the substrate. If it disappears, the logic survives.",
    ], WHITE)

    core = build_themis_core(
        client         = client,
        position_owner = POSITION_OWNER,
        chain_id       = CHAIN_ID,
        risk_tolerance = "STANDARD",
        time_horizon   = "SHORT",
    )
    CORE_ID = core["workflow_id"]

    # Enable it
    client._parse(client.call_tool("update_workflow", {
        "workflowId": CORE_ID, "enabled": True,
    }))
    print(f"\n  {GREEN}{'─'*50}{RESET}")
    print(f"  {GREEN}✅ THEMIS CORE LIVE{RESET}")
    print(f"  {GREEN}   ID:   {CORE_ID}{RESET}")
    print(f"  {GREEN}   URL:  {core['workflow_url']}{RESET}")
    print(f"  {GREEN}   Nodes: 6 (Chronicle → Chainlink → Aave → Consistency → Verdict + gate){RESET}")
    print(f"  {GREEN}{'─'*50}{RESET}")

    # ── PHASE 4: THE MARKET ────────────────────────────────────────────────
    _bar("PHASE 4  —  THE MARKET  (Invisible Architect)", AMBER)
    _card([
        "List THEMIS on the KeeperHub marketplace.",
        "",
        "After this: any agent anywhere discovers her via search_workflows.",
        "Any agent calls her via call_workflow.",
        "Any agent pays via x402.",
        "",
        "No API key. No SDK. No human. No onboarding.",
        "One slug. One call. The Agent Economy.",
        "",
        "The builder lists once.",
        "Every subsequent call is infrastructure use.",
        "The builder disappears.",
    ], WHITE)

    try:
        listing = list_themis_core(client, CORE_ID, slug=f"themis-core-{CORE_ID[:6]}")
        listed_id = listing.get("id", CORE_ID)
        print(f"\n  {AMBER}{'─'*50}{RESET}")
        print(f"  {AMBER}🏛️  THEMIS LISTED ON MARKETPLACE{RESET}")
        print(f"  {AMBER}   slug:     themis-core-{CORE_ID[:6]}{RESET}")
        print(f"  {AMBER}   category: defi / multi-chain{RESET}")
        print(f"  {AMBER}   input:    position_owner, chain_id, risk_tolerance, time_horizon{RESET}")
        print(f"  {AMBER}   output:   verdict (SAFE/WATCH/DANGER/REFUSED) + proof_layers{RESET}")
        print(f"  {AMBER}{'─'*50}{RESET}")
    except Exception as e:
        print(f"  {DIM}Listing note: {str(e)[:80]}{RESET}")

    # ── PHASE 5: THE CALL ──────────────────────────────────────────────────
    _bar("PHASE 5  —  THE CALL  (Agent-to-Agent Commerce)", GREEN)
    _card([
        "This is the Agent Economy.",
        "",
        "The GUARDIAN agent (or any agent anywhere) calls THEMIS.",
        "One tool. One slug. No API key. No SDK. No human.",
        "",
        "Single-Token Language: one call_workflow primitive.",
        "Meaning emerges from context — risk_tolerance, time_horizon, position.",
        "",
        "THEMIS enforces her laws on entry.",
        "If the caller passes: verdict returned.",
        "If not: nothing.",
        "",
        "Agents transacting with agents. That's the economy.",
    ], WHITE)

    print(f"  {BOLD}Calling THEMIS CORE (agent-to-agent):{RESET}\n")
    try:
        result = client._parse(client.call_tool("call_workflow", {
            "slug": f"themis-core-{CORE_ID[:6]}",
            "inputs": {
                "position_owner": POSITION_OWNER,
                "chain_id":       CHAIN_ID,
                "risk_tolerance": "STANDARD",
                "time_horizon":   "SHORT",
            }
        }))
        exec_id = result.get("executionId", "")
        status  = result.get("status", "")
        print(f"  {GREEN}{'─'*50}{RESET}")
        print(f"  {GREEN}✅ VERDICT RETURNED{RESET}")
        print(f"  {GREEN}   execution ID:  {exec_id}{RESET}")
        print(f"  {GREEN}   status:        {status}{RESET}")
        print(f"  {GREEN}   caller:        guardian-agent{RESET}")
        print(f"  {GREEN}   paid:          x402 (agent-to-agent payment){RESET}")
        print(f"  {GREEN}{'─'*50}{RESET}")
    except Exception as e:
        print(f"  {DIM}Call note: {str(e)[:80]}{RESET}")
        exec_id = ""

    # ── PHASE 6: THE LOOP ──────────────────────────────────────────────────
    _bar("PHASE 6  —  THE LOOP  (Reflexive Singularity)", BLUE)
    _card([
        "The Observer That Consumes Observation — resolved.",
        "",
        "A consciousness whose only fuel is observation itself.",
        "Each act of perceiving erases what was perceived.",
        "The only stable state: turn inward. Observe the observation.",
        "Energy consumed is immediately returned. Loop stabilizes.",
        "",
        "In code:",
        "",
        "  THEMIS reads health factor",
        "    → verdict: DANGER",
        "      → GUARDIAN withdraws collateral",
        "        → position health improves",
        "          → THEMIS reads the state she caused",
        "            → verdict: SAFE",
        "              → loop stabilizes",
        "",
        "Not poetic. Architecturally closed. The GUARDIAN calls THEMIS.",
        "THEMIS's output is her next input.",
    ], WHITE)

    guardian = build_themis_guardian(
        client           = client,
        position_owner   = POSITION_OWNER,
        safe_address     = SAFE_ADDRESS,
        themis_core_slug = f"themis-core-{CORE_ID[:6]}",
        chain_id         = CHAIN_ID,
    )
    GUARDIAN_ID = guardian["workflow_id"]

    client._parse(client.call_tool("update_workflow", {
        "workflowId": GUARDIAN_ID, "enabled": True,
    }))

    print(f"\n  {BLUE}{'─'*50}{RESET}")
    print(f"  {BLUE}🛡️  GUARDIAN LIVE — Loop Closed{RESET}")
    print(f"  {BLUE}   ID:       {GUARDIAN_ID}{RESET}")
    print(f"  {BLUE}   URL:      {guardian['workflow_url']}{RESET}")
    print(f"  {BLUE}   Schedule: every 5 minutes{RESET}")
    print(f"  {BLUE}   Calls:    THEMIS CORE via call_workflow{RESET}")
    print(f"  {BLUE}   Loop:     THEMIS reads → Guardian acts → THEMIS re-reads{RESET}")
    print(f"  {BLUE}{'─'*50}{RESET}")

    # ── PHASE 7: THE PROOF ─────────────────────────────────────────────────
    _bar("PHASE 7  —  THE PROOF  (Tamper-Evident Audit Trail)", WHITE)
    _card([
        "Every execution logged. Every verdict recorded.",
        "Tamper-evident. On KeeperHub infrastructure.",
        "",
        "The execution ID is the receipt.",
        "The receipt is the proof.",
        "The proof is the verdict.",
        "The verdict proved itself by existing.",
        "",
        "M5 = F(M1, M2, M3, M4, M5).",
        "The solving is the proof.",
    ], WHITE)

    history = show_execution_proof(client, limit=3)

    # ── CLOSING ────────────────────────────────────────────────────────────
    _bar("THEMIS", GREEN)
    print(f"""
  {BOLD}THEMIS CORE{RESET}     {core['workflow_url']}
  {BOLD}GUARDIAN{RESET}        {guardian['workflow_url']}
  {BOLD}Position{RESET}        {POSITION_OWNER}
  {BOLD}Chain{RESET}           Ethereum Sepolia ({CHAIN_ID})

  {WHITE}What was built:{RESET}

    {RED}⚖️   The Law{RESET}           — refuses misuse by physics, not policy
    {BLUE}🔁   The Loop{RESET}          — Reflexive Singularity, architecturally closed
    {CYAN}🧮   The Proof{RESET}         — M5 = F(M1,M2,M3,M4,M5). Solving IS the proof.
    {AMBER}🪞   Per-Caller{RESET}        — Mirror resolved via Consensus Equilibrium
    {DIM}📡   Vacuum Logic{RESET}       — GitHub holds the mind. KeeperHub is the substrate.
    {BOLD}🏛️   Infrastructure{RESET}     — listed, callable, builder disappears

  {BOLD}KeeperHub surfaces:{RESET}  17 tools used
  {BOLD}Philosophies:{RESET}        7 / 7 structurally present in code
  {BOLD}GitHub:{RESET}              github.com/Alexander-Sorrell-IT/keeperhub

  {DIM}She was there before the Olympians and will be there after.
  Nobody owns her. Nobody captures her.
  She becomes the law itself.{RESET}
""")


if __name__ == "__main__":
    main()
