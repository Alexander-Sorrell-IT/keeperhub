"""themis/marketplace.py

The Invisible Architect — THEMIS becomes infrastructure.

List THEMIS CORE on the KeeperHub marketplace.
Demonstrate discoverability: search_workflows finds it.
Demonstrate the Agent Economy: call_workflow invokes it.

The builder lists. Agents call. The builder disappears into the build.
Nobody thinks about who invented paper.
Once THEMIS is called by enough agents, it IS the infrastructure.
"""
from __future__ import annotations
import json, logging
import sys; sys.path.insert(0, '..')
from agent.keeperhub_client import KeeperHubClient

log = logging.getLogger(__name__)


def list_themis_core(
    client: KeeperHubClient,
    workflow_id: str,
    slug: str = "themis-core",
    quiet: bool = False,
) -> dict:
    """
    List THEMIS CORE on the KeeperHub marketplace.

    After this call:
    - Any agent can discover THEMIS via search_workflows("themis")
    - Any agent can invoke THEMIS via call_workflow(slug="themis-core")
    - THEMIS is infrastructure. The builder is invisible.
    """
    if not quiet:
        print(f"\nListing THEMIS CORE on marketplace (slug: {slug})...")
    result = client._parse(client.call_tool("list_workflow", {
        "workflowId": workflow_id,
        "slug":       slug,
        "category":   "defi",
        "chain":      "multi-chain",
        "description": (
            "THEMIS — Five-layer self-verifying DeFi verdict. "
            "Call with position_owner, chain_id, risk_tolerance, time_horizon. "
            "Returns verdict (SAFE/WATCH/DANGER/REFUSED) + proof_layers. "
            "Refuses front-run and exploit callers by law, not by filter. "
            "Self-Observing Equation: verdict proves itself. No external verifier."
        ),
        # Without an outputMapping a marketplace call returns an execution id and
        # nothing else — the caller gets no verdict back.
        "outputMapping": {
            "verdict":             "{{@layer5-verdict:Layer 5 THEMIS Verdict.direction}}",
            "health_factor":       "{{@layer3-aave-health:Layer 3 Aave Health Factor.result.healthFactor}}",
            "chronicle_price":     "{{@layer1-scale:Layer 1b Scale Chronicle.value}}",
            "chainlink_price":     "{{@layer2-scale:Layer 2b Scale Chainlink.value}}",
            "layers_reconciled":   "{{@layer4-consistency:Layer 4 Cross Source Consistency.withinTolerance}}",
            "price_deviation_pct": "{{@layer4-consistency:Layer 4 Cross Source Consistency.percentDifference}}",
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "position_owner":  {"type": "string", "description": "Wallet address to evaluate (0x...)"},
                "chain_id":        {"type": "string", "description": "Chain ID (e.g. 11155111 for Sepolia)"},
                "risk_tolerance":  {"type": "string", "enum": ["CONSERVATIVE","STANDARD","AGGRESSIVE"], "description": "Caller risk profile"},
                "time_horizon":    {"type": "string", "enum": ["SHORT","MEDIUM","LONG"], "description": "Caller time horizon"},
            },
            "required": ["position_owner"],
        },
    }))
    if not quiet:
        print(f"Listed: {json.dumps(result, indent=2, default=str)[:400]}")
    return result


def discover_themis(client: KeeperHubClient, quiet: bool = False) -> dict:
    """
    Demonstrate discoverability — search_workflows finds THEMIS.
    This is the Invisible Architect moment: the build is findable.
    """
    if not quiet:
        print("\nSearching marketplace for THEMIS...")
    result = client._parse(client.call_tool("search_workflows", {
        "query":    "themis defi verdict",
        "category": "defi",
        "chain":    "11155111",
        "sort":     "recent",
    }))
    if not quiet:
        print(f"Search result: {json.dumps(result, indent=2, default=str)[:600]}")
    return result


def agent_calls_themis(
    client: KeeperHubClient,
    slug: str,
    position_owner: str,
    risk_tolerance: str = "STANDARD",
    time_horizon: str = "SHORT",
    chain_id: str = "11155111",
    quiet: bool = False,
) -> dict:
    """
    Demonstrate agent-to-agent call — this IS the Agent Economy.

    An external agent (the Guardian, or any other agent in the world)
    calls THEMIS via call_workflow. One tool. One slug.
    No API key. No SDK. No human.

    This is Single-Token Language: one primitive, all meaning through context.
    """
    if not quiet:
        print(f"\nAgent calling THEMIS CORE (slug: {slug})...")
    if not quiet:
        print(f"  This is agent-to-agent commerce.")
    if not quiet:
        print(f"  The caller buys THEMIS's verdict.")
    if not quiet:
        print(f"  THEMIS enforces her own laws on the way in.")

    result = client._parse(client.call_tool("call_workflow", {
        "slug": slug,
        "inputs": {
            "position_owner": position_owner,
            "chain_id":       chain_id,
            "risk_tolerance": risk_tolerance,
            "time_horizon":   time_horizon,
        },
    }))
    if not quiet:
        print(f"\nVerdict received: {json.dumps(result, indent=2, default=str)[:600]}")
    return result


def show_execution_proof(client: KeeperHubClient, limit: int = 5,
                         quiet: bool = False) -> dict:
    """
    Pull execution history — tamper-evident audit trail.
    Every call to THEMIS is logged. The record is immutable.
    The Invisible Architect built infrastructure with receipts.
    """
    if not quiet:
        print("\nPulling THEMIS execution history (audit trail)...")
    result = client._parse(client.call_tool("list_executions", {
        "limit": limit,
    }))
    if not quiet:
        print(f"Executions: {json.dumps(result, indent=2, default=str)[:800]}")
    return result
