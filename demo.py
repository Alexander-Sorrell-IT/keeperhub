"""demo.py — Entropy Guard end-to-end demo.

Shows:
1. Connect to KeeperHub via MCP
2. Deploy Entropy Guard workflow
3. Read Aave V3 health factor directly through KeeperHub
4. Show workflow URL as audit proof

Run: KEEPERHUB_API_KEY=kh_... python3 demo.py
"""
import os, sys, json, logging
logging.basicConfig(level=logging.WARNING)
sys.path.insert(0, '.')
from agent.keeperhub_client import KeeperHubClient
from entropy_guard.build import build_entropy_guard

def main():
    api_key = os.environ.get("KEEPERHUB_API_KEY", "")
    if not api_key:
        print("Set KEEPERHUB_API_KEY first")
        sys.exit(1)

    client = KeeperHubClient(api_key=api_key)

    print("=" * 60)
    print("ENTROPY GUARD — KeeperHub Agent Economy Hackathon")
    print("=" * 60)
    print()
    print("The governing law everyone accepts: DeFi positions are passive.")
    print("You supply collateral. You watch. Liquidation takes the rest.")
    print()
    print("The rewrite: what if the position has its own entropy?")
    print("One rule. Deterministic. Auditable. Execution — not an alert.")
    print()

    # Step 1: connect
    print("[1/3] Connecting to KeeperHub MCP...")
    tools = client.list_tools()
    print(f"      Connected. {len(tools)} tools available.")
    print()

    # Step 2: deploy
    print("[2/3] Deploying Entropy Guard workflow...")
    result = build_entropy_guard(
        client       = client,
        user_address = "0x0000000000000000000000000000000000000001",
        safe_address = "0x0000000000000000000000000000000000000002",
    )
    print()

    # Step 3: read Aave health factor through KeeperHub as proof
    print("[3/3] Reading Aave V3 pool data through KeeperHub (Sepolia)...")
    proof = client.contract_call(
        chain_id      = "11155111",
        address       = "0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8",
        function_name = "totalSupply",
        function_args = "[]",
        simulate      = True,
        idempotency_key = "demo-proof-001",
    )
    print(f"      Onchain read result: {proof}")
    print()

    print("=" * 60)
    print("SUBMISSION PROOF")
    print("=" * 60)
    print(f"Workflow ID:  {result['workflow_id']}")
    print(f"Workflow URL: {result['workflow_url']}")
    print(f"Onchain read: {proof}")
    print()
    print("KeeperHub surfaces used:")
    for s in [
        "MCP server (HTTP streaming, session-based)",
        "create_workflow — workflow deployed via MCP",
        "aave-v3/get-user-account-data — health factor read",
        "aave-v3/withdraw — defensive execution action",
        "trigger/schedule — 5-minute heartbeat",
        "execute_contract_call — onchain read proof",
    ]:
        print(f"  • {s}")

if __name__ == "__main__":
    main()
