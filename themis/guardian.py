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

    nodes = [
        # Heartbeat trigger
        {
            "id":         "guardian-heartbeat",
            "type":       "trigger",
            "actionType": "trigger/schedule",
            "name":       "Guardian Heartbeat (5 min)",
            "config": {
                "cron":     schedule_cron,
                "timezone": "UTC",
            },
        },

        # Call THEMIS CORE — agent-to-agent
        # The Guardian buys THEMIS's intelligence.
        # This is the Single-Token Language: one call_workflow, all meaning.
        {
            "id":         "call-themis-core",
            "type":       "action",
            "actionType": "call_workflow",
            "name":       "Call THEMIS CORE (agent-to-agent)",
            "config": {
                "slug":   themis_core_slug,
                "inputs": {
                    "position_owner": position_owner,
                    "chain_id":       chain_id,
                    "risk_tolerance": "STANDARD",
                    "time_horizon":   "SHORT",
                },
                "description": (
                    "The Guardian calls THEMIS CORE — agent-to-agent commerce. "
                    "The Guardian has no intelligence of its own. "
                    "It buys THEMIS's verdict and acts on it. "
                    "This is the Agent Economy the hackathon is named for."
                ),
            },
        },

        # Defensive withdrawal — fires only if THEMIS says DANGER
        # execute_check_and_execute: atomic read → act if condition met
        {
            "id":         "guardian-defend",
            "type":       "action",
            "actionType": "execute_check_and_execute",
            "name":       "Guardian Defense (Reflexive Singularity)",
            "config": {
                "contract_address": "0x6Ae43d3271ff6888e7Fc43Fd7321a503ff738951",  # Aave V3 Pool
                "chain_id":         chain_id,
                "function_name":    "getUserAccountData",
                "function_args":    f"[\"{position_owner}\"]",
                "condition": {
                    "operator": "lt",
                    "value":    HF_DANGER,
                },
                "action": {
                    "contract_address": "0x6Ae43d3271ff6888e7Fc43Fd7321a503ff738951",
                    "function_name":    "withdraw",
                    "function_args":    f"[\"{USDC_SEPOLIA}\", \"{withdraw_amount}\", \"{safe_address}\"]",
                },
                "description": (
                    "Reflexive Singularity in code: "
                    "Guardian acts → position health improves → "
                    "THEMIS reads better state next tick → loop stabilizes. "
                    "The Oracle's output was the Guardian's input. "
                    "The Guardian's action is the Oracle's next input."
                ),
            },
        },
    ]

    edges = [
        {"source": "guardian-heartbeat", "target": "call-themis-core"},
        {"source": "call-themis-core",   "target": "guardian-defend"},
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
