# Semaphore Obsidian + Git Sync

Session-derived setup for maintaining Semaphore text materials in an Obsidian vault synced to a private GitHub repository.

## Local vault

Path:

```bash
/home/igor1/obsidian/semaphore-work
```

Created as a Markdown/Obsidian vault with:

- `00-inbox/` — quick captures and rough imports
- `01-strategy/` — GTM, positioning, pricing, packaging
- `02-sales-process/` — lead routing, qualification, trial/MAP, billing/process design
- `03-calls/` — dated call notes and debriefs
- `04-partners-customers/` — customer/account/partner notes
- `90-reference/` — stable reference docs copied from Igor OS context
- `99-archive/` — stale drafts

Reference docs initially copied:

- `semaphore-role-clarity.md`
- `semaphore-salesnav-enablement-2026-05-29.md`
- `semaphore-discovery-2026-05-14.md`
- `semaphore-gtm-insights.md`

## Git state

Initialized on `main` with initial commit:

```bash
git init -b main
git add -A
git commit -m "init: semaphore obsidian vault"
```

Remote configured:

```bash
git@github.com:IgorAms1/semaphore-work-notes.git
```

## Sync command

The vault includes `sync.sh`:

```bash
cd /home/igor1/obsidian/semaphore-work
./sync.sh
```

It stages all changes, commits with a timestamped `notes: update ...` message, and pushes.

## Private repo creation caveat

In the session, SSH auth to GitHub worked, but GitHub API/gh repo creation credentials were not available in the execution environment. If the private repo does not exist yet, Igor must create it manually:

- Owner: `IgorAms1`
- Name: `semaphore-work-notes`
- Visibility: private
- Empty repo: no README, no `.gitignore`, no license

Then push:

```bash
cd /home/igor1/obsidian/semaphore-work
git push -u origin main
```

## Privacy guardrails

Do not commit:

- API keys, tokens, `.env`, certificates, SSH keys
- raw Jamf exports or confidential company dumps
- CSV/XLSX exports unless explicitly sanitized and needed
- passwords, customer PII, private credentials

Preferred content:

- sanitized Markdown notes
- call summaries
- strategy drafts
- account notes without raw sensitive data
- templates/checklists/playbooks
