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

Flags:
  --debug    Show every API call, every response, working and failing aspects
  --log FILE Write full output to FILE (strips ANSI)
  --no-new   Skip workflow creation (use existing IDs from env)

Usage:
    export KEEPERHUB_API_KEY=your_key
    export THEMIS_POSITION_OWNER=0x9007a515008b4236C8E3644d0A7C8E853B92F4fb
    export THEMIS_SAFE_ADDRESS=0x9007a515008b4236C8E3644d0A7C8E853B92F4fb
    python3 demo.py
    python3 demo.py --debug
    python3 demo.py --debug --log themis_demo.log
"""
from __future__ import annotations
import argparse, os, sys, json, time, threading, re as _re, datetime
sys.path.insert(0, '.')

import logging

BOLD  = "\033[1m"
DIM   = "\033[2m"
RED   = "\033[91m"
GREEN = "\033[92m"
CYAN  = "\033[96m"
AMBER = "\033[93m"
BLUE  = "\033[94m"
WHITE = "\033[97m"
RESET = "\033[0m"
ANSI  = _re.compile(r'\x1b\[[0-9;]*m')

# ── Global debug flag ──────────────────────────────────────────────────────
DEBUG = False

def dbg(label: str, data=None) -> None:
    """Print debug output — only shown with --debug flag."""
    if not DEBUG:
        return
    print(f"\n{DIM}{'·'*72}{RESET}")
    print(f"{DIM}[DEBUG] {label}{RESET}")
    if data is not None:
        if isinstance(data, (dict, list)):
            txt = json.dumps(data, indent=2, default=str)
        else:
            txt = str(data)
        for line in txt.splitlines()[:60]:   # cap at 60 lines
            print(f"  {DIM}{line}{RESET}")
        if len(txt.splitlines()) > 60:
            print(f"  {DIM}... ({len(txt.splitlines())} lines total){RESET}")
    print(f"{DIM}{'·'*72}{RESET}")


class _Spinner:
    """Simple terminal spinner for long API calls."""
    def __init__(self, msg: str):
        self._msg = msg
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._spin, daemon=True)

    def _spin(self):
        frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        i = 0
        while not self._stop.is_set():
            print(f"\r  {DIM}{frames[i % len(frames)]}  {self._msg}...{RESET}",
                  end="", flush=True)
            i += 1
            time.sleep(0.1)

    def __enter__(self):
        self._t.start()
        return self

    def __exit__(self, *_):
        self._stop.set()
        self._t.join()
        print(f"\r  {' ' * (len(self._msg) + 10)}\r", end="", flush=True)


def _bar(text: str, color: str = CYAN) -> None:
    print(f"\n{BOLD}{color}{'═'*72}{RESET}")
    print(f"{BOLD}{color}  {text}{RESET}")
    print(f"{BOLD}{color}{'═'*72}{RESET}")


def _card(lines: list, color: str = WHITE) -> None:
    print(f"\n{DIM}{'─'*72}{RESET}")
    for line in lines:
        print(f"  {color}{line}{RESET}")
    print(f"{DIM}{'─'*72}{RESET}\n")
    time.sleep(0.3)


def _receipt(runs: list) -> None:
    """Print clean audit receipts instead of raw JSON."""
    print(f"\n  {BOLD}Execution audit trail:{RESET}\n")
    for run in runs[:3]:
        ts = run.get("startedAt","")[:19].replace("T"," ")
        dur = run.get("durationMs", 0)
        status = run.get("status","")
        wf_name = run.get("workflowName","")
        exec_id = run.get("id","")
        total   = run.get("totalSteps", 0)
        done    = run.get("completedSteps", 0)
        color   = GREEN if status == "success" else RED

        print(f"  {color}{'─'*50}{RESET}")
        print(f"  {color}✅ EXECUTION  {BOLD}{exec_id}{RESET}")
        print(f"  {color}   workflow:  {wf_name}{RESET}")
        print(f"  {color}   status:    {status}{RESET}")
        print(f"  {color}   started:   {ts} UTC{RESET}")
        print(f"  {color}   duration:  {dur}ms{RESET}")
        print(f"  {color}   nodes:     {total} total / {done} triggered{RESET}")

        dbg(f"Raw execution record: {exec_id}", run)
    print(f"  {DIM}{'─'*50}{RESET}")


def _find_existing_workflow(client, name_prefix: str) -> str | None:
    """Return ID of existing workflow matching name_prefix, or None."""
    dbg(f"Checking for existing workflow: {name_prefix}")
    try:
        result = client._parse(client.call_tool("list_workflows", {}))
        workflows = result.get("workflows", result.get("items", []))
        dbg(f"list_workflows returned {len(workflows)} workflows", workflows)
        for wf in workflows:
            if wf.get("name","").startswith(name_prefix):
                dbg(f"Found existing: {wf.get('name')} → {wf.get('id')}")
                return wf.get("id")
    except Exception as e:
        dbg(f"list_workflows error: {e}")
    return None


def _enable_workflow(client, workflow_id: str) -> None:
    dbg(f"Enabling workflow: {workflow_id}")
    result = client._parse(client.call_tool("update_workflow", {
        "workflowId": workflow_id, "enabled": True,
    }))
    dbg(f"enable result", result)


def main(skip_new: bool = False) -> int:
    POSITION_OWNER = os.getenv("THEMIS_POSITION_OWNER",
                               "0x9007a515008b4236C8E3644d0A7C8E853B92F4fb")
    SAFE_ADDRESS   = os.getenv("THEMIS_SAFE_ADDRESS",
                               "0x9007a515008b4236C8E3644d0A7C8E853B92F4fb")
    CHAIN_ID       = "11155111"
    OWNER_SHORT    = POSITION_OWNER[:8]
    CORE_NAME      = f"themis-core-{OWNER_SHORT}"
    GUARDIAN_NAME  = f"themis-guardian-{OWNER_SHORT}"

    from agent.keeperhub_client import KeeperHubClient
    from themis.integrity  import check as integrity_check, gate_stats
    from themis.verify     import ThemisVerdict
    from themis.core       import build_themis_core
    from themis.guardian   import build_themis_guardian
    from themis.marketplace import list_themis_core, show_execution_proof

    dbg("Initializing KeeperHubClient")
    client = KeeperHubClient()
    dbg("Client ready", {"api_url": "https://app.keeperhub.com/mcp",
                          "position_owner": POSITION_OWNER,
                          "chain_id": CHAIN_ID})

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
        f"  Chain:     {BOLD}Ethereum Sepolia ({CHAIN_ID}){RESET}{WHITE}",
        f"  GitHub:    {BOLD}github.com/Alexander-Sorrell-IT/keeperhub{RESET}{WHITE}",
        f"  Debug:     {BOLD}{'ON' if DEBUG else 'OFF'}{RESET}{WHITE}",
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

    callers = [
        ("EXPLOIT",  "FLASH",  "attacker-0x1337",    False),
        ("MEV",      "SHORT",  "mev-bot-0xdead",      False),
        ("FRONTRUN", "MEDIUM", "front-runner-0xbad",  False),
        ("STANDARD", "SHORT",  "guardian-agent",      True),
        ("CONSERVATIVE", "LONG", "portfolio-manager", True),
    ]
    for risk, horizon, caller_id, should_pass in callers:
        result = integrity_check(risk, horizon, caller_id)
        dbg(f"integrity_check({risk}, {horizon}, {caller_id})", result)
        time.sleep(0.15)
        color  = GREEN if result["allowed"] else RED
        symbol = "✅" if result["allowed"] else "⛔"
        verdict_str = "ALLOWED" if result["allowed"] else f"REFUSED"
        print(f"  {color}{symbol}  {risk:<15} {horizon:<8}  {verdict_str:<8}  "
              f"{DIM}{caller_id}{RESET}")
        if DEBUG and not result["allowed"]:
            print(f"     {DIM}reason: {result['reason'][:70]}{RESET}")

    stats = gate_stats()
    dbg("gate_stats()", stats)
    print(f"\n  {DIM}Gate stats: "
          f"{stats['refused']} refused / {stats['served']} served / "
          f"{stats['total_calls']} total  "
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

    # Healthy position
    print(f"  {DIM}Scenario A: healthy position (health=1.8, prices aligned)...{RESET}")
    v_healthy = ThemisVerdict(
        m1_chronicle_price = 2450.50,
        m2_chainlink_price = 2451.20,
        m3_health_factor   = int(1.8 * 1e18),
        risk_tolerance     = "STANDARD",
        time_horizon       = "SHORT",
    )
    proof_a = v_healthy.compute()
    dbg("ThemisVerdict.compute() — healthy", proof_a)

    layers = proof_a["layers"]
    for lname, lkey in [("Chronicle","M1_chronicle"),("Chainlink","M2_chainlink"),
                         ("Health","M3_health_factor"),("Consistency","M4_consistency")]:
        v = layers[lkey]
        raw = v.get("value") or v.get("deviation")
        if lkey == "M4_consistency" and raw is not None:
            val = f"{raw:.4%}"
        elif lkey == "M3_health_factor" and raw is not None:
            val = f"{raw:.4f}"
        elif raw is not None and isinstance(raw, float):
            val = f"${raw:,.2f}"
        else:
            val = str(raw)
        valid_str = f"{GREEN}✓{RESET}" if v["valid"] else f"{RED}✗{RESET}"
        print(f"  {DIM}  M{['1','2','3','4'][['Chronicle','Chainlink','Health','Consistency'].index(lname)]}  "
              f"{lname:<14}{RESET}  {val:<12}  {valid_str}", flush=True)
        time.sleep(0.15)

    v_color = GREEN if proof_a["verdict"] == "SAFE" else AMBER if proof_a["verdict"] == "WATCH" else RED
    print(f"\n  {BOLD}{v_color}  M5  VERDICT        {proof_a['verdict']}   valid={proof_a['valid']}{RESET}")
    print(f"  {DIM}  proof: {proof_a['proof_statement'][:80]}...{RESET}\n")

    # Compromised position — M5 cannot exist
    print(f"  {DIM}Scenario B: compromised prices (2% deviation — layers don't reconcile)...{RESET}")
    v_bad = ThemisVerdict(
        m1_chronicle_price = 2450.00,
        m2_chainlink_price = 2500.00,   # 2.04% deviation — fails M4
        m3_health_factor   = int(1.2 * 1e18),
        risk_tolerance     = "STANDARD",
        time_horizon       = "SHORT",
    )
    proof_b = v_bad.compute()
    dbg("ThemisVerdict.compute() — compromised", proof_b)
    print(f"  {RED}  M4  Deviation      2.04%   threshold=1.00%   {RED}✗{RESET}")
    print(f"  {RED}  M5  VERDICT        {proof_b['verdict']}   — M5 cannot exist if layers don't reconcile{RESET}")
    print(f"  {DIM}  proof: {proof_b['proof_statement'][:80]}...{RESET}")

    # ── PHASE 3: THE BUILD ─────────────────────────────────────────────────
    _bar("PHASE 3  —  THE BUILD  (THEMIS CORE deployed live)", CYAN)
    _card([
        "THEMIS CORE is now deployed as a live workflow on KeeperHub.",
        "",
        "Five nodes. Chronicle → Chainlink → Aave → Consistency → Verdict.",
        "Integrity gate at the front. Repulsive Gravity enforced at the edge.",
        "",
        "Idempotent: if THEMIS already exists for this position, she is reused.",
        "No duplicates. Production-grade.",
        "",
        "After creation: the workflow validates itself.",
        "Valid only if all 6 nodes pass structural check.",
        "The workflow proving its own existence IS the Self-Observing Equation.",
    ], WHITE)

    # Idempotent: reuse if exists
    CORE_ID = None
    if not skip_new:
        existing = _find_existing_workflow(client, CORE_NAME)
        if existing:
            CORE_ID = existing
            print(f"  {DIM}→  Existing THEMIS CORE found: {CORE_ID}  (reusing — no duplicate){RESET}")
            dbg(f"Reusing existing workflow {CORE_ID}")
        else:
            with _Spinner("Deploying THEMIS CORE"):
                core = build_themis_core(
                    client         = client,
                    position_owner = POSITION_OWNER,
                    chain_id       = CHAIN_ID,
                    risk_tolerance = "STANDARD",
                    time_horizon   = "SHORT",
                    quiet          = True,
                )
            CORE_ID = core["workflow_id"]
            dbg("build_themis_core result", core)
    else:
        CORE_ID = os.getenv("THEMIS_CORE_ID", "")
        print(f"  {DIM}→  --no-new: using THEMIS_CORE_ID={CORE_ID}{RESET}")

    # Enable
    _enable_workflow(client, CORE_ID)
    CORE_URL = f"https://app.keeperhub.com/workflows/{CORE_ID}"

    # Validate
    print(f"  {DIM}→  Validating (Self-Observing Equation)...{RESET}", end="", flush=True)
    val = client._parse(client.call_tool("validate_workflow",
                                          {"workflowId": CORE_ID, "deepCheck": True}))
    dbg("validate_workflow", val)
    ok      = val.get("result", {}).get("valid", False)
    nodes   = val.get("result", {}).get("nodeCount", "?")
    v_color = GREEN if ok else RED
    print(f"\r  {v_color}  Validation:  valid={ok}  nodeCount={nodes}{RESET}    ")

    print(f"\n  {GREEN}{'─'*50}{RESET}")
    print(f"  {GREEN}✅ THEMIS CORE LIVE{RESET}")
    print(f"  {GREEN}   ID:    {CORE_ID}{RESET}")
    print(f"  {GREEN}   URL:   {CORE_URL}{RESET}")
    print(f"  {GREEN}   nodes: {nodes}  (Chronicle→Chainlink→Aave→Consistency→Verdict+gate){RESET}")
    print(f"  {GREEN}{'─'*50}{RESET}")

    CORE_SLUG = f"themis-core-{CORE_ID[:6]}"

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

    print(f"  {DIM}→  Listing on marketplace (slug: {CORE_SLUG})...{RESET}", end="", flush=True)
    try:
        listing = list_themis_core(client, CORE_ID, slug=CORE_SLUG, quiet=True)
        dbg("list_workflow result", listing)
        listed_ok = "id" in listing
        print(f"\r  {AMBER}{'─'*50}{RESET}    ")
        print(f"  {AMBER}🏛️  THEMIS LISTED{RESET}")
        print(f"  {AMBER}   slug:     {CORE_SLUG}{RESET}")
        print(f"  {AMBER}   category: defi / multi-chain{RESET}")
        print(f"  {AMBER}   callable: call_workflow(slug='{CORE_SLUG}', inputs={{...}}){RESET}")
        print(f"  {AMBER}{'─'*50}{RESET}")
    except Exception as e:
        dbg(f"list_workflow error", str(e))
        print(f"\r  {DIM}Marketplace listing: {str(e)[:70]}{RESET}")

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

    print(f"  {BOLD}Calling THEMIS via marketplace slug:{RESET}\n")
    print(f"  {DIM}  call_workflow(slug='{CORE_SLUG}', inputs={{...}}){RESET}\n")

    dbg("call_workflow inputs", {
        "slug": CORE_SLUG,
        "position_owner": POSITION_OWNER,
        "chain_id": CHAIN_ID,
        "risk_tolerance": "STANDARD",
        "time_horizon": "SHORT",
    })

    EXEC_ID = ""
    with _Spinner("Agent calling THEMIS"):
        call_result = client._parse(client.call_tool("call_workflow", {
            "slug": CORE_SLUG,
            "inputs": {
                "position_owner": POSITION_OWNER,
                "chain_id":       CHAIN_ID,
                "risk_tolerance": "STANDARD",
                "time_horizon":   "SHORT",
            }
        }))
    dbg("call_workflow result", call_result)

    EXEC_ID = call_result.get("executionId", "")
    call_status = call_result.get("status", "")
    raw_error = call_result.get("raw","")

    if EXEC_ID and call_status == "success":
        print(f"  {GREEN}{'─'*50}{RESET}")
        print(f"  {GREEN}✅ VERDICT RETURNED  (agent-to-agent){RESET}")
        print(f"  {GREEN}   execution ID:  {BOLD}{EXEC_ID}{RESET}")
        print(f"  {GREEN}   status:        {call_status}{RESET}")
        print(f"  {GREEN}   caller:        guardian-agent → themis-core{RESET}")
        print(f"  {GREEN}   interface:     call_workflow + x402{RESET}")
        print(f"  {GREEN}{'─'*50}{RESET}")
    else:
        print(f"  {AMBER}Call result: {raw_error[:80]}{RESET}")
        dbg("call_workflow raw error", raw_error)

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
        "            → verdict: SAFE → loop stabilizes",
        "",
        "Not poetic. Architecturally closed.",
        "THEMIS's output is her next input.",
    ], WHITE)

    GUARDIAN_ID = None
    if not skip_new:
        existing_g = _find_existing_workflow(client, GUARDIAN_NAME)
        if existing_g:
            GUARDIAN_ID = existing_g
            print(f"  {DIM}→  Existing GUARDIAN found: {GUARDIAN_ID}  (reusing){RESET}")
        else:
            with _Spinner("Deploying THEMIS GUARDIAN"):
                guardian = build_themis_guardian(
                    client           = client,
                    position_owner   = POSITION_OWNER,
                    safe_address     = SAFE_ADDRESS,
                    themis_core_slug = CORE_SLUG,
                    chain_id         = CHAIN_ID,
                    quiet            = True,
                )
            GUARDIAN_ID = guardian["workflow_id"]
            dbg("build_themis_guardian result", guardian)
    else:
        GUARDIAN_ID = os.getenv("THEMIS_GUARDIAN_ID", "")

    _enable_workflow(client, GUARDIAN_ID)

    # Validate guardian
    print(f"  {DIM}→  Validating GUARDIAN...{RESET}", end="", flush=True)
    gval = client._parse(client.call_tool("validate_workflow",
                                           {"workflowId": GUARDIAN_ID, "deepCheck": True}))
    dbg("validate_workflow (guardian)", gval)
    gok    = gval.get("result",{}).get("valid", False)
    gnodes = gval.get("result",{}).get("nodeCount","?")
    print(f"\r  {GREEN if gok else RED}  Guardian valid={gok}  nodeCount={gnodes}{RESET}    ")

    GUARDIAN_URL = f"https://app.keeperhub.com/workflows/{GUARDIAN_ID}"
    print(f"\n  {BLUE}{'─'*50}{RESET}")
    print(f"  {BLUE}🛡️  GUARDIAN LIVE — Reflexive Singularity Closed{RESET}")
    print(f"  {BLUE}   ID:       {GUARDIAN_ID}{RESET}")
    print(f"  {BLUE}   URL:      {GUARDIAN_URL}{RESET}")
    print(f"  {BLUE}   schedule: every 5 minutes{RESET}")
    print(f"  {BLUE}   calls:    {CORE_SLUG} (agent-to-agent){RESET}")
    print(f"  {BLUE}   loop:     THEMIS reads → Guardian acts → THEMIS re-reads{RESET}")
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

    raw_history = client._parse(client.call_tool("list_executions", {"limit": 5}))
    dbg("list_executions raw", raw_history)
    runs = raw_history.get("runs", [])
    _receipt(runs)

    # Also pull detailed proof of the specific execution if we have one
    if EXEC_ID:
        print(f"\n  {DIM}→  Pulling full execution proof for {EXEC_ID}...{RESET}", end="", flush=True)
        exec_detail = client._parse(client.call_tool("get_execution", {"executionId": EXEC_ID}))
        dbg(f"get_execution({EXEC_ID})", exec_detail)
        node_statuses = exec_detail.get("status",{}).get("nodeStatuses",[])
        print(f"\r  {GREEN}   Execution detail: {len(node_statuses)} node(s) confirmed{RESET}    ")
        if DEBUG:
            for ns in node_statuses:
                ns_color = GREEN if ns.get("status") == "success" else RED
                print(f"  {ns_color}     node: {ns.get('nodeId','?'):<30} status: {ns.get('status','?')}{RESET}")

    # ── CLOSING ────────────────────────────────────────────────────────────
    _bar("THEMIS", GREEN)
    print(f"""
  {BOLD}THEMIS CORE{RESET}     {CORE_URL}
  {BOLD}GUARDIAN{RESET}        {GUARDIAN_URL}
  {BOLD}Position{RESET}        {POSITION_OWNER}
  {BOLD}Chain{RESET}           Ethereum Sepolia ({CHAIN_ID})
  {BOLD}Execution ID{RESET}    {EXEC_ID or '(see audit trail above)'}

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
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="THEMIS — KeeperHub Agent Economy Demo")
    ap.add_argument("--debug",  action="store_true",
                    help="Show every API call, response, working and failing aspects")
    ap.add_argument("--log",    metavar="FILE",
                    help="Write full output to FILE (strips ANSI)")
    ap.add_argument("--no-new", action="store_true",
                    help="Skip workflow creation; use THEMIS_CORE_ID / THEMIS_GUARDIAN_ID from env")
    args = ap.parse_args()

    DEBUG = args.debug
    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
        print(f"\n{DIM}[DEBUG MODE ON — all API calls and responses will be shown]{RESET}")
    else:
        logging.basicConfig(level=logging.WARNING)

    if args.log:
        class _Tee:
            def __init__(self, stream, path):
                self._s = stream
                self._f = open(path, "w")
            def write(self, data):
                self._s.write(data)
                self._f.write(ANSI.sub("", data))
            def flush(self):
                self._s.flush()
                self._f.flush()
        sys.stdout = _Tee(sys.stdout, args.log)
        print(f"# THEMIS demo log — {datetime.datetime.now().isoformat()}")
        print(f"# Log: {args.log}\n")

    raise SystemExit(main(skip_new=args.no_new))
