# Skill design notes from Vas3k article

Source: https://vas3k.club/post/31627/ (`Born to Skill: как перестать материться на агента бессонными ночами`)

## Useful takeaways

- A skill is a reusable behavior module, not just a long prompt. It should encode when to activate, what to do, what files/scripts/templates to use, and how to verify completion.
- The frontmatter `description` is the trigger hook. Too short: the agent misses it. Too broad: false positives and context noise. Write descriptions as practical activation conditions.
- Good skills use progressive disclosure: keep the always-loaded `SKILL.md` concise; move long examples, source notes, domain details, and troubleshooting into `references/`.
- Skills become more powerful when they ship reusable assets: `scripts/` for deterministic probes/actions, `templates/` for repeatable output/file shapes, `references/` for deeper domain notes.
- Prefer maintaining a small class-level skill library over installing many narrow or foreign workflow skills. Borrow structure and ideas from outside skills, but audit scripts and adapt instructions to the user's actual workflow.
- Skills should improve themselves: repeated failures or corrections should become patches, pitfalls, validators, templates, or reference notes.

## Igor OS implication

For Igor OS, prioritize class-level modes (`morning`, `work`, `avoidance`, `training`, `mindmap`, etc.) with rich references over one-off session skills. Personal procedures belong in skills; durable facts belong in memory.