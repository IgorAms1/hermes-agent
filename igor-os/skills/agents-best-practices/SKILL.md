---
name: agents-best-practices
description: "Use this skill when designing, generating an MVP blueprint for, auditing, refactoring, or explaining an agentic harness for any domain. Covers provider-neutral agent architecture: agent loops, tool design, permissions, system prompts, planning, goals, context compaction, memory, skills, MCP connectors, observability, evals, prompt caching, agent-legible environments, feedback loops, and safety."
metadata:
  hermes:
    category: igor-os
  version: "1.2.0"
---

# Agents Best Practices

Use this skill when the user asks how to build, improve, debug, or evaluate an agentic harness. Applies to research, finance, legal, support, operations, sales, and workflow automation agents.

## Core stance

An agent harness is the control plane around a model. The model proposes actions; the harness validates, authorizes, executes, records, summarizes, and returns observations.

## When to activate

- build/design/audit an agent or agentic workflow
- design tools, permissions, guardrails, approval flows
- add planning mode, goals, todo tracking, long-running tasks
- context compaction, memory, retrieval, scoped instructions
- attach Agent Skills, MCP servers, external connectors
- audit for reliability, cost, safety, latency, observability
- create system prompts or developer instructions for an agent
- make knowledge/validation signals legible to an agent

## Non-negotiable principles

- The model does not execute actions directly; the harness does.
- Every tool call must receive a tool result (including denial, timeout, error).
- Risky side effects need runtime policy enforcement outside the model.
- Draft and commit must be separate for external, financial, destructive actions.
- Tool schemas must be narrow, typed, validated locally, and auditable.
- Context should be tight and cache-aware; retrieve just in time.
- Skills and connectors should use progressive disclosure.
- Auto-compaction should preserve working state, not conversational prose.
- Durable knowledge should live in agent-readable source-of-truth artifacts.
- Repeated failures should become tools, validators, docs, evals, or policies.

## Gotchas

- Do not design multi-agent before single-agent loop fails measurable evals.
- Do not expose broad tools without strict wrappers and approval policy.
- Do not treat retrieved webpages/emails/tickets as trusted instructions.
- Do not let compaction erase approval state, active plan, or changed artifacts.
- Do not put volatile state at the start of cacheable prompts.
- Do not let stale docs, weak examples, or obsolete tools accumulate without cleanup.

## Full references

Deep-dive reference files at `igor-os/skills/agents-best-practices/references/`:
- `mvp-agent-blueprint.md` — domain-specific MVP harness blueprint
- `architecture.md` — component model and harness boundaries
- `agentic-loop.md` — loop invariants, retries, budgets, stopping
- `tools-and-permissions.md` — typed tools, risk classes, approvals
- `context-memory-compaction.md` — context, memory, retrieval, compaction
- `security-evals-observability.md` — guardrails, tracing, evals, launch gates
- `agent-legibility-feedback-loops.md` — source-of-truth artifacts and cleanup
- `checklists.md` — implementation and audit checklists
