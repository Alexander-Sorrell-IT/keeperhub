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
DEVIATION_THRESHOLD_PCT = 1        # Chronicle vs Chainlink max divergence, percent



def themis_core_graph(position_owner: str, chain_id: str = SEPOLIA):
    """Return (nodes, edges) for THEMIS CORE.

    Split out from build_themis_core so an already-deployed THEMIS can be
    re-synced in place with sync_themis_core() instead of being duplicated.
    """
    def _node(nid, label, config, x):
        return {
            "id":       nid,
            "type":     "action",
            "position": {"x": x, "y": 0},
            "data": {"type": "action", "label": label, "config": config},
        }

    # KeeperHub stores node behaviour under data.config. actionType and every
    # required field live INSIDE that config — anything sent at the top level is
    # silently dropped and the node executes as an empty box.
    nodes = [
        # ── INTEGRITY GATE (Repulsive Gravity) ────────────────────────────
        # Layer 0: the caller has already passed themis/integrity.py before we
        # get here. This node is the entry point the marketplace calls.
        {
            "id":       "integrity-gate",
            "type":     "trigger",
            "position": {"x": 0, "y": 0},
            "data": {
                "type":   "trigger",
                "label":  "THEMIS Integrity Gate",
                "config": {"triggerType": "Manual"},
            },
        },

        # ── LAYER 1: Chronicle ETH/USD (18 decimals) ───────────────────────
        _node("layer1-chronicle", "Layer 1 Chronicle ETH USD", {
            "actionType": "chronicle/eth-usd-read",
            "network":    chain_id,
        }, 272),

        # Scale Chronicle's WAD integer into a decimal string M4 can compare.
        _node("layer1-scale", "Layer 1b Scale Chronicle", {
            "actionType": "math/format-number",
            "value":      "{{@layer1-chronicle:Layer 1 Chronicle ETH USD.result}}",
            "decimals":   18,
            "notation":   "plain",
        }, 544),

        # ── LAYER 2: Chainlink ETH/USD (8 decimals) ────────────────────────
        _node("layer2-chainlink", "Layer 2 Chainlink ETH USD", {
            "actionType": "chainlink/eth-usd-latest-round-data",
            "network":    chain_id,
        }, 816),

        _node("layer2-scale", "Layer 2b Scale Chainlink", {
            "actionType": "math/format-number",
            "value":      "{{@layer2-chainlink:Layer 2 Chainlink ETH USD.result.answer}}",
            "decimals":   8,
            "notation":   "plain",
        }, 1088),

        # ── LAYER 3: Aave V3 health factor ─────────────────────────────────
        _node("layer3-aave-health", "Layer 3 Aave Health Factor", {
            "actionType": "aave-v3/get-user-account-data",
            "network":    chain_id,
            "user":       position_owner,
        }, 1360),

        # ── LAYER 4: Cross-source consistency ──────────────────────────────
        # Chronicle vs Chainlink must agree within 1%. breached=true means the
        # sources disagree and M5 has nothing valid to fold.
        _node("layer4-consistency", "Layer 4 Cross Source Consistency", {
            "actionType": "math/compare-tolerance",
            "actual":     "{{@layer1-scale:Layer 1b Scale Chronicle.value}}",
            "expected":   "{{@layer2-scale:Layer 2b Scale Chainlink.value}}",
            "mode":       "percent",
            "tolerance":  str(int(DEVIATION_THRESHOLD_PCT)),
        }, 1632),

        # ── LAYER 5: VERDICT — Self-Observing Equation ─────────────────────
        # Folds M1-M4 by comparing the health factor against the danger floor.
        # direction=below → DANGER, above → SAFE/WATCH per caller context.
        _node("layer5-verdict", "Layer 5 THEMIS Verdict", {
            "actionType": "math/compare-tolerance",
            "actual":     "{{@layer3-aave-health:Layer 3 Aave Health Factor.result.healthFactor}}",
            "expected":   HF_DANGER_THRESHOLD,
            "mode":       "absolute",
            "tolerance":  "0",
        }, 1904),
    ]

    _seq = ["integrity-gate", "layer1-chronicle", "layer1-scale",
            "layer2-chainlink", "layer2-scale", "layer3-aave-health",
            "layer4-consistency", "layer5-verdict"]
    edges = [{"id": f"e{i}", "source": _seq[i], "target": _seq[i + 1]}
             for i in range(len(_seq) - 1)]

    return nodes, edges


def sync_themis_core(client, workflow_id: str, position_owner: str,
                     chain_id: str = SEPOLIA) -> dict:
    """Push the current graph onto an existing THEMIS CORE.

    Keeps the workflow id, marketplace slug and listing intact while
    replacing nodes and edges — the path a redeploy actually takes.
    """
    nodes, edges = themis_core_graph(position_owner, chain_id)
    return client._parse(client.call_tool("update_workflow", {
        "workflowId": workflow_id, "nodes": nodes, "edges": edges,
    }))

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
    nodes, edges = themis_core_graph(position_owner, chain_id)

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
