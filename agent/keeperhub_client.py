"""keeperhub_client.py — HTTP client for the KeeperHub MCP server.

KeeperHub MCP endpoint: https://app.keeperhub.com/mcp
Auth: Bearer token via KEEPERHUB_API_KEY env var.

Pattern mirrors argus/agent/splunk_mcp_client.py — same JSON-RPC shape,
different transport (HTTP streamable vs Splunk management port).
"""
from __future__ import annotations
import os, json, logging, requests
from typing import Optional

log = logging.getLogger(__name__)

KH_MCP_URL  = os.getenv("KEEPERHUB_MCP_URL", "https://app.keeperhub.com/mcp")
KH_API_KEY  = os.getenv("KEEPERHUB_API_KEY", "")


class KeeperHubClient:
    """Thin HTTP client for the KeeperHub MCP server.

    Exposes the three surfaces we need:
      - create_workflow(nodes, edges)  -> workflow_id
      - dry_run(workflow_id, inputs)   -> simulated execution result
      - execute(workflow_id, inputs)   -> tx_hash + audit receipt
    """

    def __init__(self, api_key: str = KH_API_KEY, mcp_url: str = KH_MCP_URL):
        if not api_key:
            raise ValueError("KEEPERHUB_API_KEY not set")
        self.api_key  = api_key
        self.mcp_url  = mcp_url.rstrip("/")
        self._req_id  = 0
        self._initialized = False

    # ── auth header ────────────────────────────────────────────────────
    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
            "Accept":        "application/json",
        }

    # ── JSON-RPC core ──────────────────────────────────────────────────
    def _rpc(self, method: str, params: Optional[dict] = None) -> dict:
        self._req_id += 1
        body = {
            "jsonrpc": "2.0",
            "id":      self._req_id,
            "method":  method,
        }
        if params is not None:
            body["params"] = params
        r = requests.post(self.mcp_url, headers=self._headers,
                          json=body, timeout=60)
        r.raise_for_status()
        resp = r.json()
        if "error" in resp:
            raise RuntimeError(f"KeeperHub MCP error: {resp['error']}")
        return resp.get("result", {})

    def _ensure_init(self):
        if self._initialized:
            return
        self._rpc("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities":    {},
            "clientInfo":      {"name": "argus-keeperhub", "version": "1.0"},
        })
        self._initialized = True

    def call_tool(self, name: str, arguments: Optional[dict] = None) -> dict:
        self._ensure_init()
        return self._rpc("tools/call", {"name": name, "arguments": arguments or {}})

    def list_tools(self) -> list[dict]:
        self._ensure_init()
        return self._rpc("tools/list", {}).get("tools", [])

    # ── workflow surfaces ──────────────────────────────────────────────
    def create_workflow(self, name: str, description: str,
                        nodes: list[dict], edges: list[dict]) -> str:
        """Create a workflow. Returns workflow_id."""
        result = self.call_tool("create_workflow", {
            "name":        name,
            "description": description,
            "nodes":       nodes,
            "edges":       edges,
        })
        content = result.get("content", [])
        for c in content:
            if c.get("type") == "text":
                try:
                    payload = json.loads(c["text"])
                    return payload.get("id") or payload.get("workflowId", "")
                except Exception:
                    pass
        raise RuntimeError(f"create_workflow: no id in response: {result}")

    def dry_run(self, workflow_id: str, inputs: dict) -> dict:
        """Dry run — simulate without touching the chain."""
        result = self.call_tool("dry_run_workflow", {
            "workflowId": workflow_id,
            "inputs":     inputs,
        })
        return self._parse_content(result)

    def execute(self, workflow_id: str, inputs: dict) -> dict:
        """Execute the workflow. Returns tx_hash + audit receipt."""
        result = self.call_tool("execute_workflow", {
            "workflowId": workflow_id,
            "inputs":     inputs,
        })
        return self._parse_content(result)

    def get_run(self, run_id: str) -> dict:
        """Get the audit receipt for a completed run."""
        result = self.call_tool("get_run", {"runId": run_id})
        return self._parse_content(result)

    # ── helpers ────────────────────────────────────────────────────────
    @staticmethod
    def _parse_content(result: dict) -> dict:
        for c in result.get("content", []):
            if c.get("type") == "text":
                try:
                    return json.loads(c["text"])
                except Exception:
                    return {"raw": c["text"]}
        return result
