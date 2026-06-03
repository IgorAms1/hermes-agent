# Semaphore GTM Insights (May 2026)

## 4-Motion Framework (Vika call, 28 May)

Semaphore needs **4 motions, not 2** (PRO vs Enterprise):

| Motion | Description | Qualification |
|---|---|---|
| **PRO self-service** | Lightweight, low-touch, credit card | No sales needed |
| **Mid-market / Production** | Qualified but not enterprise-heavy | Use case, production risk, teams, procurement, support expectations |
| **Enterprise / Regulated** | Compliance, HA/DR, air-gap, SLA, RBAC | Pricing by scope/risk, not nodes |
| **MSP** | Partner using as managed service | End customer has no console access; separate licensing model |

### PRO Pricing — Broken Signals

- Too cheap
- No real limits on nodes
- Billing by users/runners leaves loopholes
- Small clients chase custom contracts/legal that don't cover the cost

**Fix:** Introduce meaningful limits at PRO tier. Gate enterprise features (HA/DR, air-gap, RBAC) behind scope/risk assessment, not node count.

### Enterprise Pricing Principle

Price by **scope/risk** not nodes:
- Production criticality
- HA/DR requirements
- Air-gapped license
- Multi-team usage
- SLA/support tier
- Custom legal
- Role mapping / RBAC
- Regulated use / compliance

### ICP Shift

**From:** generic DevOps
**To:** infrastructure teams, legacy-heavy companies, fintech, retail, regional infrastructure, support/self-service automation, controlled execution without full access

---

## Inbound Signal Patterns

### 1. Customer with Ready PR (Adfinis)
Adfinis came with a *ready PR for chart auth/Vault integration before purchasing*. This is a positive signal:
- Validates product-market fit (they invested engineering time)
- Indicates production intent (not just tire-kicking)
- Recommendation: treat as qualified lead, merge PR fast, use as community proof

### 2. Strategic AE asking on behalf of client (Trace3)
Strategic AE at a partner inquiring about Semaphore for a specific client = **customer pull**, not abstract interest.
- Partner wants to know if they can make margin on implementation/resale
- Semaphore fills a portfolio gap (lighter alternative to AAP, etc.)
- Recommendation: treat as partner/integrator motion, not direct sale

---

## Call Output Template (Semaphore-specific)

Use for calls with Semaphore team:

```text
Problems confirmed
1.
2.
3.

Positioning that landed
-

Next concrete action
-

Leads/referrals surfaced
-
```

---

## Partner / MSP Motion (Katya call, 28 May)

Two parallel tracks confirmed:
1. **Partner-led resale/referral** — traditional channel
2. **MSP/managed service** — partner uses Semaphore to deliver services

**Current phase:** DO NOT build a full partner program. Instead:
- **Partner One-Pager v0.1** — pilot partner motion for sourced opportunities
- Together qualify, together sell
- Partner gets clear margin/discount
- After 2-3 deals, review model
- No PowerPoint, no legal, no MDF upfront
