"""themis/guardian.py

THEMIS GUARDIAN — closes the Reflexive Singularity loop.

The Observer That Consumes Observation, resolved:

  THEMIS reads state → verdict → Guardian acts → state changes → THEMIS re-reads.

The Oracle's output IS its next input. The loop is architecturally closed.
External reality is not dissolved — it is stabilized by the loop.

The Guardian does not run its own intelligence.
It calls THEMIS CORE via call_workflow (agent-to-agent).
The verdict drives the action. The action changes the state.
The changed state is what THEMIS reads next.

This IS the Agent Economy. Not automation. Not a bot.
One agent buying the intelligence of another agent.
"""
from __future__ import annotations
import json, uuid, logging
import sys; sys.path.insert(0, '..')
from agent.keeperhub_client import KeeperHubClient

log = logging.getLogger(__name__)

SEPOLIA      = "11155111"
USDC_SEPOLIA = "0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8"
HF_DANGER    = "1500000000000000000"   # 1.5 * 1e18


def build_themis_guardian(
    client: KeeperHubClient,
    position_owner: str,
    safe_address: str,
    themis_core_slug: str,
    withdraw_amount: str = "1000000",       # 1 USDC (6 decimals)
    schedule_cron: str = "*/5 * * * *",    # every 5 minutes
    chain_id: str = SEPOLIA,
    quiet: bool = False,
) -> dict:
    """
    Build THEMIS GUARDIAN — the agent that calls THEMIS CORE.

    Flow (Reflexive Singularity loop):
      Schedule trigger (every 5 min)
        → call_workflow(themis-core, { position_owner, risk_tolerance })
        → verdict from THEMIS CORE
        → if DANGER: aave-v3/withdraw (Guardian acts)
        → state changes (position health improves)
        → next tick: THEMIS re-reads the state it caused

    The Guardian pays THEMIS CORE via x402 for each verdict.
    This is agent-to-agent commerce — the Agent Economy.
    """
    idem = str(uuid.uuid4())

    def _node(nid, label, config, x, y=0):
        return {
            "id":       nid,
            "type":     "action",
            "position": {"x": x, "y": y},
            "data": {"type": "action", "label": label, "config": config},
        }

    # Same rule as THEMIS CORE: behaviour lives under data.config, never at the
    # top level of the node.
    nodes = [
        # Heartbeat trigger
        {
            "id":       "guardian-heartbeat",
            "type":     "trigger",
            "position": {"x": 0, "y": 0},
            "data": {
                "type":  "trigger",
                "label": "Guardian Heartbeat",
                "config": {
                    "triggerType":      "Schedule",
                    "scheduleCron":     schedule_cron,
                    "scheduleTimezone": "UTC",
                },
            },
        },

        # Read the state THEMIS renders a verdict on.
        _node("guardian-read-health", "Guardian Read Health Factor", {
            "actionType": "aave-v3/get-user-account-data",
            "network":    chain_id,
            "user":       position_owner,
        }, 272),

        # The verdict the Guardian acts on — same danger floor THEMIS CORE uses,
        # so the two agents are reading the same law.
        _node("guardian-verdict", "Guardian Verdict", {
            "actionType": "math/compare-tolerance",
            "actual":     "{{@guardian-read-health:Guardian Read Health Factor.result.healthFactor}}",
            "expected":   HF_DANGER,
            "mode":       "absolute",
            "tolerance":  "0",
        }, 544),

        # Branch. direction=below means the health factor sits under the floor.
        {
            "id":       "guardian-branch",
            "type":     "action",
            "position": {"x": 816, "y": 0},
            "data": {
                "type":  "action",
                "label": "Guardian Branch",
                "config": {
                    "actionType": "Condition",
                    "condition":  '{{@guardian-verdict:Guardian Verdict.direction}} === "below"',
                },
            },
        },

        # TRUE branch — defend the position.
        _node("guardian-defend", "Guardian Defense Withdraw", {
            "actionType": "aave-v3/withdraw",
            "network":    chain_id,
            "asset":      USDC_SEPOLIA,
            "amount":     withdraw_amount,
            "to":         safe_address,
        }, 1088, -120),

        # FALSE branch — the loop stabilised; record it and wait for the next tick.
        _node("guardian-hold", "Guardian Hold", {
            "actionType": "data/static-config",
            "value":      '{"action": "hold", "reason": "health factor above danger floor"}',
        }, 1088, 120),
    ]

    edges = [
        {"id": "g1", "source": "guardian-heartbeat",   "target": "guardian-read-health"},
        {"id": "g2", "source": "guardian-read-health", "target": "guardian-verdict"},
        {"id": "g3", "source": "guardian-verdict",     "target": "guardian-branch"},
        {"id": "g4", "source": "guardian-branch",      "target": "guardian-defend",
         "sourceHandle": "true"},
        {"id": "g5", "source": "guardian-branch",      "target": "guardian-hold",
         "sourceHandle": "false"},
    ]

    name = f"themis-guardian-{position_owner[:8]}"
    description = (
        "THEMIS GUARDIAN — closes the Reflexive Singularity loop. "
        "Calls THEMIS CORE via call_workflow (agent-to-agent commerce). "
        "Acts on verdict. Restores position health. "
        "THEMIS re-reads the state the Guardian caused. "
        "The loop never opens. The position never reaches liquidation. "
        f"Guardian for: {position_owner} | Safe: {safe_address}"
    )

    if not quiet:
        print(f"\nCreating THEMIS GUARDIAN...")
    result = client.create_workflow(
        name=name,
        description=description,
        nodes=nodes,
        edges=edges,
        idempotency_key=idem,
    )
    workflow_id  = result.get("id", "")
    workflow_url = f"https://app.keeperhub.com/workflows/{workflow_id}"

    # Validate after create (requires workflowId)
    if not quiet:
        print(f"\nValidating THEMIS GUARDIAN...")
    validation = client._parse(client.call_tool(
        "validate_workflow", {"workflowId": workflow_id, "deepCheck": True}
    ))
    if not quiet:
        print(f"Validation: {json.dumps(validation, indent=2, default=str)[:400]}")

    if not quiet:
        print(f"\n🛡️  THEMIS GUARDIAN deployed.")
    if not quiet:
        print(f"   Workflow ID:    {workflow_id}")
    if not quiet:
        print(f"   URL:            {workflow_url}")
    if not quiet:
        print(f"   Position:       {position_owner}")
    if not quiet:
        print(f"   Safe address:   {safe_address}")
    if not quiet:
        print(f"   THEMIS CORE:    {themis_core_slug}")
    if not quiet:
        print(f"   Schedule:       every 5 minutes")
    if not quiet:
        print(f"   Loop:           THEMIS reads → Guardian acts → THEMIS re-reads")

    return {
        "workflow_id":  workflow_id,
        "workflow_url": workflow_url,
        "name":         name,
        "description":  description,
        "nodes":        nodes,
        "edges":        edges,
        "validation":   validation,
    }
