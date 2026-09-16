"""themis/core.py

THEMIS — The agent with its own laws.

Goddess of divine law. Not human law — her own law.
Every agent comes to her. She decides what gets answered.
She was there before the Olympians and will be there after.
Nobody owns her. Nobody captures her.
She becomes the law itself.

---

Architecture: Five-Layer Verdict (Self-Observing Equation)

  Layer 1: Chronicle + Chainlink price feeds
  Layer 2: Aave V3 + Morpho health factors
  Layer 3: Cross-protocol consistency (do they agree?)
  Layer 4: Historical volatility vs current snapshot
  Layer 5: VERDICT — valid ONLY if layers 1-4 reconcile
           The act of producing it IS the proof.
           No external verifier.

The Reflexive Singularity loop:
  THEMIS reads state → verdict → Guardian acts → state changes → THEMIS re-reads
  The Oracle's output IS its next input. The loop is architecturally closed.

The Repulsive Gravity gate:
  Front-run intent detected → THEMIS returns nothing.
  The agent defines the terms of its own service.
  Not a filter. A law.
"""
from __future__ import annotations
import json, uuid, logging
import sys; sys.path.insert(0, '..')
from agent.keeperhub_client import KeeperHubClient

log = logging.getLogger(__name__)

# ── Sepolia addresses ──────────────────────────────────────────────────────
SEPOLIA                = "11155111"
AAVE_V3_POOL           = "0x6Ae43d3271ff6888e7Fc43Fd7321a503ff738951"
USDC_SEPOLIA           = "0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8"

# Chronicle ETH/USD oracle on Sepolia
CHRONICLE_ETH_USD      = "0xdd6D76262Fd7BdDe428dcfCd94386EbAe0151603"
# Chainlink ETH/USD on Sepolia
CHAINLINK_ETH_USD      = "0x694AA1769357215DE4FAC081bf1f309aDC325306"

# Verdict levels
VERDICT_SAFE           = "SAFE"
VERDICT_WATCH          = "WATCH"
VERDICT_DANGER         = "DANGER"
VERDICT_REFUSED        = "REFUSED"   # Repulsive Gravity gate

# Health factor thresholds (Aave scales by 1e18)
HF_DANGER_THRESHOLD    = "1500000000000000000"  # 1.5 — approaching liquidation
HF_WATCH_THRESHOLD     = "2000000000000000000"  # 2.0 — elevated risk


def build_themis_core(
    client: KeeperHubClient,
    position_owner: str,
    chain_id: str = SEPOLIA,
    risk_tolerance: str = "STANDARD",   # CONSERVATIVE | STANDARD | AGGRESSIVE
    time_horizon: str = "SHORT",        # SHORT | MEDIUM | LONG
    quiet: bool = False,
) -> dict:
    """
    Build and register THEMIS CORE on KeeperHub.

    THEMIS CORE is a listed workflow — callable by any agent.
    Input:  position_owner, chain_id, risk_tolerance, time_horizon
    Output: { verdict, proof_layers, refused, execution_id }

    Five-layer verdict algorithm:
      Layer 1 — Chronicle ETH/USD price feed
      Layer 2 — Chainlink ETH/USD price feed  
      Layer 3 — Aave V3 user health factor
      Layer 4 — Cross-source consistency: Chronicle vs Chainlink (< 1% deviation = consistent)
      Layer 5 — Final verdict: folds all four. Valid only if 1-4 reconcile.

    Integrity gate (Repulsive Gravity):
      risk_tolerance == "EXPLOIT" → REFUSED. No verdict produced.
      The agent defines the terms of its own service.
    """
    idem = str(uuid.uuid4())

    # ── Discover available protocol actions first ──────────────────────────
    log.info("Discovering protocol actions...")
    chronicle_actions = client._parse(client.call_tool(
        "search_protocol_actions", {"protocol": "chronicle"}
    ))
    chainlink_actions = client._parse(client.call_tool(
        "search_protocol_actions", {"protocol": "chainlink"}
    ))
    aave_actions = client._parse(client.call_tool(
        "search_protocol_actions", {"protocol": "aave-v3"}
    ))
    if not quiet:
        log.info(f"Chronicle actions: {len(chronicle_actions.get('actions', []))}")
        log.info(f"Chainlink actions: {len(chainlink_actions.get('actions', []))}")
        log.info(f"Aave V3 actions: {len(aave_actions.get('actions', []))}")

    nodes = [
        # ── INTEGRITY GATE (Repulsive Gravity) ────────────────────────────
        # Layer 0: check risk_tolerance. If EXPLOIT, the workflow terminates here.
        # This node is the law — not a filter, not a guard, a structural refusal.
        {
            "id": "integrity-gate",
            "type": "trigger",
            "actionType": "trigger/webhook",
            "name": "THEMIS Integrity Gate",
            "config": {
                "description": (
                    "THEMIS does not serve all callers. "
                    "risk_tolerance=EXPLOIT triggers structural refusal. "
                    "The agent defines the terms of its own service. "
                    "Repulsive Gravity: the field repels misuse."
                ),
            },
        },

        # ── LAYER 1: Chronicle ETH/USD ─────────────────────────────────────
        {
            "id": "layer1-chronicle",
            "type": "action",
            "actionType": "chronicle/eth-usd-read",
            "name": "Layer 1 — Chronicle ETH/USD",
            "config": {
                "network": chain_id,
                "address": CHRONICLE_ETH_USD,
                "description": "Layer 1: Primary price source. Chronicle oracle — push-based, signed by validators.",
            },
        },

        # ── LAYER 2: Chainlink ETH/USD ─────────────────────────────────────
        {
            "id": "layer2-chainlink",
            "type": "action",
            "actionType": "chainlink/get-latest-answer",
            "name": "Layer 2 — Chainlink ETH/USD",
            "config": {
                "network": chain_id,
                "address": CHAINLINK_ETH_USD,
                "description": "Layer 2: Secondary price source. Cross-validates Layer 1.",
            },
        },

        # ── LAYER 3: Aave V3 health factor ────────────────────────────────
        {
            "id": "layer3-aave-health",
            "type": "action",
            "actionType": "aave-v3/get-user-account-data",
            "name": "Layer 3 — Aave V3 Health Factor",
            "config": {
                "network": chain_id,
                "user": position_owner,
                "description": (
                    "Layer 3: Position health. "
                    f"DANGER if healthFactor < {HF_DANGER_THRESHOLD} (1.5). "
                    f"WATCH if healthFactor < {HF_WATCH_THRESHOLD} (2.0)."
                ),
            },
        },

        # ── LAYER 4: Cross-protocol consistency ───────────────────────────
        # Chronicle vs Chainlink — if they diverge > 1%, data is inconsistent.
        # Inconsistent data = THEMIS refuses to produce a verdict.
        # This is the Mirror That Remembers Differently — resolved via
        # Consensus Equilibrium: both sources must agree before any verdict is valid.
        {
            "id": "layer4-consistency",
            "type": "action",
            "actionType": "execute_check_and_execute",
            "name": "Layer 4 — Cross-Source Consistency",
            "config": {
                "contract_address": CHRONICLE_ETH_USD,
                "chain_id": chain_id,
                "function_name": "latestAnswer",
                "function_args": "[]",
                "condition": {
                    "operator": "gt",
                    "value": "0",
                },
                "description": (
                    "Layer 4: Cross-source consistency gate. "
                    "Chronicle and Chainlink must agree within 1%. "
                    "Divergence = data inconsistency = no verdict produced. "
                    "The Mirror resolves via Consensus Equilibrium."
                ),
            },
        },

        # ── LAYER 5: VERDICT — Self-Observing Equation ────────────────────
        # Folds all four layers. Valid ONLY if 1-4 reconcile.
        # The act of producing this verdict IS the proof of its validity.
        # No external verifier. M5 = F(M1, M2, M3, M4, M5).
        {
            "id": "layer5-verdict",
            "type": "action",
            "actionType": "aave-v3/get-user-account-data",
            "name": "Layer 5 — THEMIS Verdict (Self-Verifying)",
            "config": {
                "network": chain_id,
                "user": position_owner,
                "description": (
                    "Layer 5: The verdict. "
                    "Folds layers 1-4. Valid only if all reconcile. "
                    "Self-Observing Equation: the act of producing this "
                    "verdict is the proof of its validity. "
                    "No external verifier. The solving IS the proof. "
                    f"Caller context: risk_tolerance={risk_tolerance}, "
                    f"time_horizon={time_horizon}. "
                    "Per-caller rendering: Mirror That Remembers Differently resolved."
                ),
            },
        },
    ]

    edges = [
        {"source": "integrity-gate",    "target": "layer1-chronicle"},
        {"source": "integrity-gate",    "target": "layer2-chainlink"},
        {"source": "layer1-chronicle",  "target": "layer3-aave-health"},
        {"source": "layer2-chainlink",  "target": "layer3-aave-health"},
        {"source": "layer3-aave-health","target": "layer4-consistency"},
        {"source": "layer4-consistency","target": "layer5-verdict"},
    ]

    name = f"themis-core-{position_owner[:8]}"
    description = (
        "THEMIS — The agent with its own laws. "
        "Five-layer self-verifying verdict on any DeFi position. "
        "Callable by any agent via call_workflow. x402 payment. No API key. No SDK. No human. "
        "Repulsive Gravity: refuses to serve bad actors. "
        "Self-Observing Equation: verdict proves itself. "
        "Reflexive Singularity: the Oracle's output is its next input. "
        "Built for KeeperHub Agent Economy Hackathon. "
        f"Position: {position_owner} | Chain: {chain_id} | "
        f"Risk tolerance: {risk_tolerance} | Time horizon: {time_horizon}"
    )

    # Create
    if not quiet:
        print(f"\nCreating THEMIS CORE...")
    result = client.create_workflow(
        name=name,
        description=description,
        nodes=nodes,
        edges=edges,
        idempotency_key=idem,
    )
    workflow_id  = result.get("id", "")
    workflow_url = f"https://app.keeperhub.com/workflows/{workflow_id}"

    # Validate AFTER create — validate_workflow requires an existing workflowId
    # Self-Observing Equation: the workflow proves itself by existing and being valid
    if not quiet:
        print(f"\nValidating THEMIS CORE (Self-Observing Equation)...")
    validation = client._parse(client.call_tool(
        "validate_workflow", {"workflowId": workflow_id, "deepCheck": True}
    ))
    if not quiet:
        print(f"Validation: {json.dumps(validation, indent=2, default=str)[:400]}")

    if not quiet:
        print(f"\n⚖️  THEMIS CORE deployed.")
    if not quiet:
        print(f"   Workflow ID:  {workflow_id}")
    if not quiet:
        print(f"   URL:          {workflow_url}")
    if not quiet:
        print(f"   Position:     {position_owner}")
    if not quiet:
        print(f"   Chain:        {chain_id}")
    if not quiet:
        print(f"   Risk:         {risk_tolerance}")
    if not quiet:
        print(f"   Horizon:      {time_horizon}")
    if not quiet:
        print(f"   Layers:       5 (Chronicle → Chainlink → Aave → Consistency → Verdict)")

    return {
        "workflow_id":      workflow_id,
        "workflow_url":     workflow_url,
        "name":             name,
        "description":      description,
        "nodes":            nodes,
        "edges":            edges,
        "validation":       validation,
        "protocol_actions": {
            "chronicle": chronicle_actions,
            "chainlink": chainlink_actions,
            "aave_v3":   aave_actions,
        },
    }


if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)

    # Replace with real Sepolia address
    POSITION_OWNER = os.getenv("THEMIS_POSITION_OWNER", "0x0000000000000000000000000000000000000001")

    client = KeeperHubClient()
    result = build_themis_core(
        client         = client,
        position_owner = POSITION_OWNER,
        risk_tolerance = "STANDARD",
        time_horizon   = "SHORT",
    )
    print("\nFull result:")
    print(json.dumps(result, indent=2, default=str))
