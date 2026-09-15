# Entropy Guard

**A self-defending Aave V3 position. Built for the KeeperHub Agent Economy Hackathon.**

`https://app.keeperhub.com/workflows/jyu598b8atmg1a7s89eyr`

---

## The idea

The governing law everyone accepts: DeFi positions are passive.
You supply collateral. You watch. You react when it's too late.
Liquidation is the gravity that pulls everything down.

**The rewrite:** What if the position has its own entropy?
What if it observes its own decay and reverses it before it collapses?

One rule. One primitive. Expressed through KeeperHub:

```
every 5 minutes:
  read health_factor from Aave V3
  if health_factor < 1.5:
    withdraw collateral to safe address
```

That's Entropy Guard. Not an alert. Not a notification. **Execution.**

---

## How it works

```
Schedule trigger (every 5 min)
  → aave-v3/get-user-account-data   [reads health factor]
  → condition: healthFactor < 1.5
  → aave-v3/withdraw                [pulls collateral to safe address]
```

The human approves the workflow once. KeeperHub executes it exactly as approved —
every 5 minutes, forever. Nothing re-inferred. Deterministic. Auditable.

---

## KeeperHub surfaces used

- `create_workflow` — builds the guard workflow via MCP
- `aave-v3/get-user-account-data` — reads health factor natively
- `aave-v3/withdraw` — executes defensive withdrawal
- `trigger/schedule` — heartbeat every 5 minutes
- Audit trail — every execution logged, tamper-evident

---

## Philosophy

| Problem | Resolution |
|---|---|
| **Repulsive Gravity Universe** — rewrite the governing law | Liquidation is gravity. We don't fight it — we remove it by acting first |
| **Single-Token Language** — one primitive, infinite expression | One rule (`if health < X → withdraw`) expresses any defensive strategy |
| **Observer That Consumes Observation** — reflexive singularity | The workflow observes the position. The observation feeds the position, not destroys it |
| **iphone.rtf** — ship before anyone else | Everyone has liquidation alerts. Nobody has self-executing defense |

> *"Physics says push harder. Physics says you didn't try hard enough."*

---

## Run it

```bash
pip install -r requirements.txt
export KEEPERHUB_API_KEY=your_key_here

# Deploy Entropy Guard for your address
python3 entropy_guard/build.py

# Or use the demo runner
python3 demo.py
```

---

## Files

| File | What it does |
|---|---|
| `entropy_guard/build.py` | Builds + deploys the workflow on KeeperHub |
| `agent/keeperhub_client.py` | MCP session client |
| `demo.py` | End-to-end demo: deploy → read health → show proof |
| `philosophy/` | The cognitive architecture behind the build |
