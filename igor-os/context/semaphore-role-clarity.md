# Semaphore Role Clarity — Igor + Katya + Nikita

*Draft for discussion, 29 May 2026*

## Goal

Убрать размытость зон ответственности. Катя не должна выбирать между Игорем и Никитой. Каждый знает, за что отвечает, где пересекаются, кто решает.

---

## RACI

| Активность | Katya | Nikita | Igor |
|------------|-------|--------|------|
| Inbound lead triage (Intercom → CRM) | **A/R** | C | C |
| Inbound lead enrichment (LinkedIn intel) | **R** | C | I |
| Technical signal validation (GitHub, job posts, blogs) | I | **R** | I |
| Buying committee mapping | **R** | C | C |
| Account prioritization / scoring | **R** | I | C |
| Commercial outreach / founder-led dialogue | **A/R** | I | C (coaching) |
| Discovery calls — commercial | **R** | C | C |
| Discovery calls — technical deep-dive | I | **R** | I |
| Pricing / packaging / proposal structure | C | I | **R** |
| Deal strategy (scope, risk, buying process) | C | I | **R** |
| Deal support — customer/partner calls (material involvement) | C | C | **R** (per deal) |
| Sales process design / GTM architecture | C | I | **R** |
| Partner motion design | C | I | **R** |
| Enablement / training materials | C | I | **R** |
| Sales Navigator list architecture & searches | **R** | I | C |
| Technical presales — demo, architecture validation | C | **R** | I |
| Support triage (OSS community → paid support path) | I | **R** | I |
| ToU / legal / procurement paperwork | **A/R** | I | C |
| Internal product feedback (from sales signals) | C | **R** | I |
| Hiring — Go developer | **A/R** | C | C (network) |

**A** = Accountable (ответственный за результат)  
**R** = Responsible (делает работу)  
**C** = Consulted (даёт инпут до решения)  
**I** = Informed (получает результат)

---

## Igor — Scope Guardrail

Igor делает:
- GTM, pricing, packaging, positioning
- Sales process, lead routing, qualification criteria
- Partner motion design
- Deal strategy and coaching
- Deal support где реально materially involved (discovery+qualification+pricing+proposal+calls)
- Weekly sync / training

Igor НЕ делает:
- Не отвечает на Intercom
- Не пишет код
- Не делает техподдержку
- Не управляет CRM (но консультирует)
- Не управляет ежедневной операционкой

## Nikita — Role Definition

Nikita:
- Technical validation inbound leads (GitHub, job posts, engineering blogs → подтвердить/опровергнуть техническую гипотезу)
- Support triage — отделяет community/free от paid/support
- Architecture validation — отвечает на технические вопросы на calls
- Demo — проводит technical deep-dive по запросу
- Product feedback loop — собирает технические сигналы от leads/calls в product backlog
- Взаимодействие с Денисом по техническим вопросам

## Katya — Role Definition

Katya:
- Commercial lead всей воронки
- Inbound triage и enrichment
- Account prioritization и outreach
- Founder-led commercial dialogue
- CRM ownership
- ToU / legal / procurement
- Hiring

## Key Principles

1. **Igor не заменяет Никиту.** Если вопрос технический — идёт к Никите. Игорь подключается к сделке по приглашению Кати, когда нужна deal strategy, pricing или coaching.

2. **Никита — technical anchor для Кати.** Когда Кате нужно проверить техническую гипотезу (реально ли клиенту нужно то, о чём он спрашивает), ответ у Никиты, не у Игоря.

3. **Igor — commercial/strategy anchor.** Когда Кате нужно построить структуру сделки, понять pricing, подготовить proposal, решить как позиционировать — ответ у Игоря.

4. **Пересечение только по конкретной сделке.** На discovery call могут быть и Катя, и Никита, и иногда Игорь. Но роли на звонке распределены заранее: кто ведёт commercial, кто technical, кто strategy.

5. **Катя принимает решения.** RACI показывает кто accountable. В спорных ситуациях решение за Катей. Игорь и Никита — advisors.
