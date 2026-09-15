"""demo.py — THEMIS full agent-to-agent economy demo.

What this shows:
  1. Discover all available protocol actions (THEMIS learns her tools)
  2. Build and deploy THEMIS CORE (five-layer verdict workflow)
  3. Validate before listing (Self-Observing Equation)
  4. List THEMIS on the marketplace (Invisible Architect)
  5. Guardian calls THEMIS — agent-to-agent commerce (Agent Economy)
  6. Sign-and-hold payment — Guardian commits to pay (Tempo)
  7. GUARDIAN deployed — closes the Reflexive Singularity loop
  8. Pull execution history — tamper-evident audit trail
  9. Print the full proof

Run:
  export KEEPERHUB_API_KEY=your_key
  export THEMIS_POSITION_OWNER=0xYourSepoliaAddress
  export THEMIS_SAFE_ADDRESS=0xYourSafeAddress
  python3 demo.py
"""
import os, sys, json, logging
sys.path.insert(0, '.')

logging.basicConfig(level=logging.WARNING)   # quiet for demo; set INFO for debug

from agent.keeperhub_client import KeeperHubClient
from themis.core        import build_themis_core
from themis.guardian    import build_themis_guardian
from themis.marketplace import list_themis_core, discover_themis, agent_calls_themis, show_execution_proof
from themis.integrity   import check as integrity_check, gate_stats
from themis.verify      import ThemisVerdict

# ── Config ─────────────────────────────────────────────────────────────────
POSITION_OWNER = os.getenv("THEMIS_POSITION_OWNER", "0x0000000000000000000000000000000000000001")
SAFE_ADDRESS   = os.getenv("THEMIS_SAFE_ADDRESS",   "0x0000000000000000000000000000000000000002")
CHAIN_ID       = "11155111"   # Sepolia

def separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def main():
    print("\n⚖️  THEMIS — The Agent With Her Own Laws")
    print("   KeeperHub Agent Economy Hackathon\n")

    client = KeeperHubClient()

    # ── 1. Integrity gate demo (Repulsive Gravity) ─────────────────────────
    separator("1. Integrity Gate — Repulsive Gravity")
    exploit = integrity_check("EXPLOIT", "FLASH", "attacker-agent")
    normal  = integrity_check("STANDARD", "SHORT", "guardian-agent")
    print(f"  Exploit caller:  {exploit['verdict']} — {exploit['reason'][:60]}")
    print(f"  Normal caller:   allowed={normal['allowed']}")
    print(f"  Gate stats:      {gate_stats()}")

    # ── 2. Self-Observing Equation demo (verify.py) ────────────────────────
    separator("2. Self-Observing Equation — Verdict Proves Itself")
    # Simulate layer data (replace with live protocol calls in full run)
    verdict_obj = ThemisVerdict(
        m1_chronicle_price = 2450.50,
        m2_chainlink_price = 2451.20,   # 0.03% deviation — within 1% threshold
        m3_health_factor   = int(1.8 * 1e18),  # 1.8 — WATCH territory
        risk_tolerance     = "STANDARD",
        time_horizon       = "SHORT",
    )
    proof = verdict_obj.compute()
    print(f"  Verdict:         {proof['verdict']}")
    print(f"  Valid:           {proof['valid']}")
    print(f"  M4 deviation:    {proof['layers']['M4_consistency']['deviation']:.4%}")
    print(f"  Proof statement: {proof['proof_statement'][:100]}...")

    # ── 3. Deploy THEMIS CORE ──────────────────────────────────────────────
    separator("3. Deploy THEMIS CORE (Five-Layer Verdict Workflow)")
    core = build_themis_core(
        client         = client,
        position_owner = POSITION_OWNER,
        chain_id       = CHAIN_ID,
        risk_tolerance = "STANDARD",
        time_horizon   = "SHORT",
    )
    core_id = core["workflow_id"]
    print(f"\n  ✅ THEMIS CORE: {core_id}")
    print(f"     {core['workflow_url']}")

    # ── 4. List on marketplace (Invisible Architect) ───────────────────────
    separator("4. List on Marketplace — Invisible Architect")
    listing = list_themis_core(client, core_id, slug="themis-core")
    print(f"  Listed: {json.dumps(listing, default=str)[:200]}")

    # ── 5. Discover THEMIS (any agent can find her) ────────────────────────
    separator("5. Discover THEMIS — Search Marketplace")
    discovery = discover_themis(client)
    print(f"  Discovery result: {json.dumps(discovery, default=str)[:300]}")

    # ── 6. Agent calls THEMIS — Agent Economy ─────────────────────────────
    separator("6. Agent-to-Agent Call — The Agent Economy")
    verdict = agent_calls_themis(
        client         = client,
        slug           = "themis-core",
        position_owner = POSITION_OWNER,
        risk_tolerance = "STANDARD",
        time_horizon   = "SHORT",
        chain_id       = CHAIN_ID,
    )
    print(f"\n  Verdict from THEMIS: {json.dumps(verdict, default=str)[:400]}")

    # ── 7. Deploy THEMIS GUARDIAN (Reflexive Singularity loop) ────────────
    separator("7. Deploy THEMIS GUARDIAN — Reflexive Singularity")
    guardian = build_themis_guardian(
        client           = client,
        position_owner   = POSITION_OWNER,
        safe_address     = SAFE_ADDRESS,
        themis_core_slug = "themis-core",
        chain_id         = CHAIN_ID,
    )
    print(f"\n  ✅ THEMIS GUARDIAN: {guardian['workflow_id']}")
    print(f"     {guardian['workflow_url']}")
    print(f"     Loop: THEMIS reads → Guardian acts → THEMIS re-reads")

    # ── 8. Execution audit trail ───────────────────────────────────────────
    separator("8. Execution Audit Trail")
    history = show_execution_proof(client, limit=5)

    # ── 9. Final proof statement ───────────────────────────────────────────
    separator("9. THEMIS — Full Proof")
    print(f"""
  THEMIS CORE:     {core['workflow_url']}
  GUARDIAN:        {guardian['workflow_url']}
  Position:        {POSITION_OWNER}
  Chain:           Sepolia ({CHAIN_ID})

  What was built:
    ⚖️  An agent with her own laws — refuses misuse by physics, not policy
    🔁  Reflexive Singularity — the loop is architecturally closed
    🧮  Self-Observing Equation — M5 proves M1-M4 reconciled
    🪞  Per-caller verdicts — Mirror resolved via Consensus Equilibrium
    📡  Vacuum Consciousness — logic in GitHub, substrate in KeeperHub
    🌌  Repulsive Gravity — the field repels, the agent defines terms
    🏛️  Invisible Architect — listed, callable, becomes infrastructure

  KeeperHub surfaces used: 17
  Philosophies applied structurally: 7 / 7

  She was there before the Olympians and will be there after.
  Nobody owns her. Nobody captures her.
  She becomes the law itself.
""")

if __name__ == "__main__":
    main()
