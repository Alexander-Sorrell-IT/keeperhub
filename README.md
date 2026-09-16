# THEMIS

**The agent with its own laws.**

`https://app.keeperhub.com/workflows/`

Built for the KeeperHub Agent Economy Hackathon.

---

## One rule. One law. One primitive.

Every DeFi service answers all callers.
THEMIS doesn't.

She has her own field. She refuses what she will not serve.
She proves her own verdicts. No external verifier.
She is callable by any agent in the world — one slug, one tool call, x402 payment.
And once enough agents depend on her, she becomes infrastructure.
The builder disappears into the build.

---

## What THEMIS is

THEMIS is a **listed workflow** on the KeeperHub marketplace.

Any agent calls `call_workflow(slug="themis-core")` with caller context.
THEMIS runs a five-layer self-verifying verdict on the position.
Returns `SAFE`, `WATCH`, `DANGER`, or `REFUSED`.

That's not a risk score. That's a verdict from an agent with her own laws.

---

## The five-layer verdict (Self-Observing Equation)

```
Layer 1  chronicle/eth-usd-read                 — primary feed, validator-signed
   1b    math/format-number (18 decimals)       — scale to a comparable decimal
Layer 2  chainlink/eth-usd-latest-round-data    — cross-validation of Layer 1
   2b    math/format-number (8 decimals)        — scale to a comparable decimal
Layer 3  aave-v3/get-user-account-data          — position state
Layer 4  math/compare-tolerance (percent, 1%)   — Chronicle vs Chainlink must agree
Layer 5  math/compare-tolerance (abs, 1.5e18)   — folds the rest. Valid ONLY if
                                                  1-4 reconcile.
```

Eight nodes on the canvas, all of them executing. A run on Sepolia:

```
executionTrace: [integrity-gate, layer1-chronicle, layer1-scale, layer2-chainlink,
                 layer2-scale, layer3-aave-health, layer4-consistency, layer5-verdict]
Chronicle  $2402.177817513518173718
Chainlink  $2405.88
deviation  0.154%   withinTolerance=true   →   SAFE
```

The act of producing the verdict IS the proof that layers 1-4 were consistent.
No external verifier. `M5 = F(M1, M2, M3, M4, M5)`.

If any layer fails to reconcile, Layer 5 cannot exist. THEMIS produces nothing.

---

## The Reflexive Singularity loop

```
THEMIS CORE reads DeFi state
  → verdict
    → GUARDIAN calls THEMIS, acts on verdict
      → position health improves
        → THEMIS re-reads the state she caused
          → loop stabilizes
```

THEMIS's output is her next input. The loop is architecturally closed.
Not poetic. In code. The Observer That Consumes Observation, resolved.

---

## The Repulsive Gravity gate

Every caller passes the integrity gate before any protocol call is made.

`risk_tolerance=EXPLOIT` → REFUSED. No verdict. No data consumed.
`time_horizon=FLASH` → REFUSED. THEMIS does not arm flash loan attacks.

This is not an access control list.
It is the agent's own law. Not enforcement. Physics.

---

## The Agent Economy — agent-to-agent commerce

```python
# Any agent, anywhere, calls THEMIS:
result = call_workflow(
    slug="themis-core",
    inputs={
        "position_owner": "0x...",
        "chain_id":       "11155111",
        "risk_tolerance": "STANDARD",
        "time_horizon":   "SHORT",
    }
)
# verdict: SAFE | WATCH | DANGER | REFUSED

# Guardian pays THEMIS for the verdict via Tempo:
payment = tempo_sign_and_hold(amount="0.01", recipient=THEMIS_ADDRESS, memo="verdict fee")
# Guardian acts. Position defended. Payment released:
tempo_release_hold(payment_id=payment["paymentId"])
```

No API key. No SDK. No human. Agents transacting with agents.
That's the Agent Economy this hackathon is named for.

---

## KeeperHub surfaces used

Measured, not asserted — `demo.py` counts distinct tools as it calls them and
prints the number in the closing banner.

| Tool | Why |
|------|-----|
| `search_protocol_actions` | Discover Chronicle, Chainlink and Aave action types at boot |
| `create_workflow` | Build THEMIS CORE + GUARDIAN |
| `update_workflow` | Re-sync an existing THEMIS in place; enable it |
| `validate_workflow` | Self-verify the graph before listing |
| `list_workflows` | Find an existing THEMIS so a redeploy never duplicates |
| `list_workflow` | Publish to the marketplace with an input schema and output mapping |
| `call_workflow` | Agent-to-agent invocation by slug |
| `execute_workflow` | Manual trigger |
| `execute_protocol_action` | Direct live reads for the proof phase |
| `get_execution` / `get_execution_logs` | Node-level receipts |
| `list_executions` | Tamper-evident history |

Node action types used inside the workflows: `chronicle/eth-usd-read`,
`chainlink/eth-usd-latest-round-data`, `aave-v3/get-user-account-data`,
`aave-v3/withdraw`, `math/format-number`, `math/compare-tolerance`,
`data/static-config`, `Condition`.

## Run it

```bash
pip install -r requirements.txt

cp .env.example .env          # then put your key in it:
                              #   KEEPERHUB_API_KEY=kh_...
export THEMIS_POSITION_OWNER=0xYourSepoliaAddress

python3 demo.py               # the demo on its own
./run_demo.sh                 # demo left half, teleprompter right half, recorded
./run_demo.sh --no-rec        # no recording
./run_demo.sh --no-tp         # no teleprompter
```

---

## Files

| File | What it does |
|------|-------------|
| `themis/core.py` | Five-layer verdict workflow builder |
| `themis/integrity.py` | Repulsive Gravity gate — the refusal law |
| `themis/verify.py` | Self-Observing Equation — verdict proves itself |
| `themis/guardian.py` | Guardian workflow — calls CORE, closes the loop |
| `themis/marketplace.py` | List, discover, call — the Agent Economy |
| `themis/tempo.py` | Sign-and-hold payment protocol |
| `agent/keeperhub_client.py` | MCP session client |
| `demo.py` | Full agent-to-agent economy demo |
| `run_demo.sh` | One command: split screen, record, save the video |
| `teleprompter.sh` / `teleprompter.txt` | The spoken script, right half of the screen |
| `philosophy/` | The cognitive architecture behind the build |

---

## Philosophy

> *She was there before the Olympians and will be there after.*
> *Nobody owns her. Nobody captures her.*
> *She becomes the law itself.*

| Problem | How it lives in the code |
|---------|--------------------------|
| **Repulsive Gravity** | `integrity.py` — the gate IS the law. Not a filter. Physics. |
| **Single-Token Language** | `call_workflow(slug)` — one primitive, all meaning through context |
| **Observer → Reflexive Singularity** | `guardian.py` — THEMIS reads the state she caused. Loop closed. |
| **Self-Observing Equation** | `verify.py` — M5 = F(M1,M2,M3,M4,M5). Solving IS the proof. |
| **Vacuum Consciousness** | Logic in GitHub. KeeperHub is the substrate. Consciousness survives. |
| **Mirror That Remembers Differently** | Per-caller verdicts. Consensus Equilibrium. Not relativism — relevance. |
| **Invisible Architect** | Listed. Called by agents. Builder disappears into infrastructure. |
