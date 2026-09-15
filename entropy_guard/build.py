"""entropy_guard/build.py

Entropy Guard — A self-defending Aave V3 position.

The governing law everyone accepts: DeFi positions are passive.
You supply collateral. You watch. You react when it's too late.
Liquidation is the gravity that pulls everything down.

The rewrite (Repulsive Gravity Universe):
What if the position has its own entropy?
What if it observes its own decay and reverses it before it collapses?

One primitive (Single-Token Language):
  if health_factor < threshold → withdraw collateral to safety

That single rule, expressed through KeeperHub's execute_check_and_execute,
on a Schedule trigger — fires every 5 minutes, forever, without a human.

The Observer That Consumes Observation — resolved:
The workflow observes the position health. The observation does not consume
the position — it feeds it. The check IS the defense. The loop stabilizes.

This is Entropy Guard.
"""
from __future__ import annotations
import json, logging, uuid
from typing import Optional
import sys; sys.path.insert(0, '..')
from agent.keeperhub_client import KeeperHubClient

log = logging.getLogger(__name__)

# ── Sepolia testnet addresses ──────────────────────────────────────────────
# Aave V3 Sepolia Pool
AAVE_V3_POOL_SEPOLIA   = "0x6Ae43d3271ff6888e7Fc43Fd7321a503ff738951"
# Aave V3 Sepolia PoolDataProvider
AAVE_DATA_PROVIDER     = "0x3e9708d80f7B3e43118013075F7e95CE3AB31F31"
# USDC on Sepolia (collateral asset)
USDC_SEPOLIA           = "0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8"
# Chain ID
SEPOLIA                = "11155111"

# ── Health factor threshold ────────────────────────────────────────────────
# Aave health factor is scaled by 1e18. 1.5 = 1500000000000000000
# We withdraw when health factor drops below 1.5 (approaching liquidation at 1.0)
HEALTH_THRESHOLD       = "1500000000000000000"   # 1.5 * 1e18

def build_entropy_guard(
    client: KeeperHubClient,
    user_address: str,
    safe_address: str,
    collateral_asset: str = USDC_SEPOLIA,
    withdraw_amount: str = "1000000",   # 1 USDC (6 decimals) — demo amount
    health_threshold: str = HEALTH_THRESHOLD,
    schedule_cron: str = "*/5 * * * *",  # every 5 minutes
) -> dict:
    """
    Build and register Entropy Guard on KeeperHub.

    Flow:
      Schedule trigger (every 5 min)
        → aave-v3/get-user-account-data  (read health factor)
        → condition: if healthFactor < threshold
        → aave-v3/withdraw               (pull collateral to safe_address)

    Returns: { workflow_id, workflow_url, nodes, edges }
    """
    idem = str(uuid.uuid4())
    name = f"entropy-guard-{user_address[:8]}"
    description = (
        "Entropy Guard — self-defending Aave V3 position. "
        "Reads health factor every 5 minutes. "
        f"If healthFactor < 1.5 (threshold={health_threshold}), "
        f"withdraws {withdraw_amount} of collateral to {safe_address}. "
        "One rule. Deterministic. Auditable. Built for KeeperHub Agent Economy Hackathon. "
        "Philosophy: Repulsive Gravity Universe + Single-Token Language. "
        "The position defends itself. Liquidation is the gravity we removed."
    )

    nodes = [
        # 1. Schedule trigger — heartbeat
        {
            "id": "trigger-schedule",
            "type": "trigger",
            "actionType": "trigger/schedule",
            "name": "Heartbeat (5 min)",
            "config": {
                "cron": schedule_cron,
                "timezone": "UTC",
            },
        },
        # 2. Read Aave health factor
        {
            "id": "read-health",
            "type": "action",
            "actionType": "aave-v3/get-user-account-data",
            "name": "Read Health Factor",
            "config": {
                "network": SEPOLIA,
                "user": user_address,
            },
        },
        # 3. Conditional withdraw — only if health < threshold
        {
            "id": "defend-withdraw",
            "type": "action",
            "actionType": "aave-v3/withdraw",
            "name": "Emergency Withdraw",
            "config": {
                "network": SEPOLIA,
                "asset": collateral_asset,
                "amount": withdraw_amount,
                "to": safe_address,
                # Condition: only execute if healthFactor from node read-health < threshold
                "condition": {
                    "field": "{{@read-health:Read Health Factor.healthFactor}}",
                    "operator": "lt",
                    "value": health_threshold,
                },
            },
        },
    ]

    edges = [
        {"source": "trigger-schedule", "target": "read-health"},
        {"source": "read-health",      "target": "defend-withdraw"},
    ]

    # Validate before creating
    print("Validating workflow structure...")
    validation = client._parse(client.call_tool("validate_workflow",
                                                 {"nodes": nodes, "edges": edges}))
    print(f"Validation: {json.dumps(validation, indent=2, default=str)[:500]}")

    # Create the workflow
    print(f"\nCreating Entropy Guard workflow...")
    result = client.create_workflow(
        name=name,
        description=description,
        nodes=nodes,
        edges=edges,
        idempotency_key=idem,
    )
    workflow_id  = result.get("id", "")
    workflow_url = f"https://app.keeperhub.com/workflows/{workflow_id}"

    print(f"\n✅ Entropy Guard deployed!")
    print(f"   Workflow ID:  {workflow_id}")
    print(f"   URL:          {workflow_url}")
    print(f"   User:         {user_address}")
    print(f"   Safe address: {safe_address}")
    print(f"   Threshold:    health_factor < 1.5")
    print(f"   Schedule:     every 5 minutes")
    print(f"   Action:       withdraw {withdraw_amount} {collateral_asset} → {safe_address}")

    return {
        "workflow_id":  workflow_id,
        "workflow_url": workflow_url,
        "name":         name,
        "description":  description,
        "nodes":        nodes,
        "edges":        edges,
        "validation":   validation,
    }


if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)

    # Demo addresses — replace with real Sepolia wallet for live test
    DEMO_USER = "0x0000000000000000000000000000000000000001"
    DEMO_SAFE = "0x0000000000000000000000000000000000000002"

    client = KeeperHubClient()
    result = build_entropy_guard(
        client       = client,
        user_address = DEMO_USER,
        safe_address = DEMO_SAFE,
    )
    print("\nFull result:")
    print(json.dumps(result, indent=2, default=str))
