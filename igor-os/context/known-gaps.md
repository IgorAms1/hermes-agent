# Igor OS Known Gaps

Acknowledged limitations and weaknesses. Review during `/cleanup` or `/weekly`.

## Structural

| Gap | Impact | Mitigation |
|---|---|---|
| Only basic overlay regression fixtures | Tool/docs drift is now checked, but output quality regressions can still slip through | `tests/igor_os/test_overlay_contracts.py`; add behavioral golden cases later |
| No mechanical enforcement of timezone conversion | "Don't quote UTC" is prompt-only, not enforced | Memory rule is the current guard |
| No automated skill activation testing | Some skills may have broken triggers that go unnoticed | Manual `/mode` invocation |
| Cron delivery target fragility | Bare platform names fail silently (see evening skill pitfall) | Docs now use `telegram:<chat_id>`; keep regression coverage |

## Content

| Gap | Impact | Mitigation |
|---|---|---|
| Limited Dutch vocabulary in memory | `/dutch` mode works but may repeat | Add phrases as Igor encounters them |
| No personal-profile.local.md yet | Some personalization is generic | Use placeholders; Igor fills in over time |
| Semaphore discovery may age | 8-9mo sales cycle means context document gets stale | Last updated May 2026; review quarterly |

## Workflow

| Gap | Impact | Mitigation |
|---|---|---|
| No automatic garbage collection | Stale memory/skills/cron accumulate | `/cleanup` mode added May 2026 |
| Evening capture relies on Telegram session search | Misses context if sessions compressed | `delegate_task` fallback documented |
| No offline/async task support | Tasks dependent on Igor's reply can stall | Clarify tool for timeouts |

## Last Reviewed

2026-05-17 — added basic overlay contract tests and documented remaining behavioral eval gap.
