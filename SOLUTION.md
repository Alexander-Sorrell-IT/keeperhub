# SOLUTION — KeeperHub Agent Economy Hackathon

> *"Build like you are building an iPhone. If you made an iPhone and released it years
> before anyone else, that is a win."* — iphone.rtf

---

## The impossible problem this build solves

**Problem:** DeFi anomaly detection is useless without execution. `argus` detects
cross-chain anomalies, classifies them with a deterministic rule engine, and stops.
The verdict sits in a log. Nothing happens.

**Paradox:** An agent that executes onchain is probabilistic. The more autonomy you
give it, the less you trust it with your funds. The less autonomy, the more human
review defeats the point. The loop eats itself.

---

## The rewrite — Observer That Consumes Observation, resolved

Separate *composition* from *execution*. The agent (argus) composes the workflow
through KeeperHub's MCP server. The human reviews it. Dry run — no chain touch.
Then KeeperHub executes that exact workflow. Nothing re-inferred at execution time.
The deterministic verdict is preserved end to end.

The agent observes and proposes. KeeperHub executes without re-observing.
Observation loop closes at review, not execution.

---

## Integration — argus + KeeperHub

### Current flow
```
on-chain event → ingestion → Foundation-Sec triage →
deterministic rule engine → verdict logged → STOP
```

### New flow
```
on-chain event → ingestion → Foundation-Sec triage →
deterministic rule engine → verdict →
KeeperHub MCP: compose workflow →
human review + dry run →
KeeperHub executes → transaction hash → audit receipt
```

### KeeperHub surfaces used
- **MCP server** — argus composes workflow as an MCP tool call
- **Dry run** — no chain touch until approved
- **Audit trail** — every run logged, tamper-evident
- New file: `agent/keeperhub_executor.py` — wraps KeeperHub MCP client
- New file: `agent/workflow_builder.py` — maps argus verdict → KeeperHub workflow

---

## Bounty (separate BUIDL — $500)

New KeeperHub trigger node: webhook/Splunk alert → KeeperHub workflow.
Any external monitoring stack can trigger execution. PR to `github.com/keeperhub/keeperhub`.

---

## Philosophy applied

| Principle | How it shows up |
|---|---|
| **iphone.rtf** — ship before anyone else | Working demo + real testnet transaction by Sep 18 |
| **Observer That Consumes Observation** | Agent composes, KeeperHub executes — loops separated |
| **Deterministic verdict** | argus rule engine owns the verdict; KeeperHub runs it exactly |
| **Self-Observing Equation** | Audit trail = workflow verifying itself through execution |

---

## Build checklist

- [ ] Fork argus, add `agent/keeperhub_executor.py`
- [ ] Wire KeeperHub MCP server
- [ ] Map argus verdict types → KeeperHub workflow specs
- [ ] Dry run on testnet
- [ ] Real transaction executed (testnet)
- [ ] Demo video (< 3 min)
- [ ] DoraHacks BUIDL submitted before Sep 18 06:00 CDT
- [ ] Separate BUIDL for bounty PR
