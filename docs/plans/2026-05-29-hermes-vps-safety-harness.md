# Hermes VPS Safety Harness Runbook

Goal: make future Hermes security changes reversible before enforcement work starts. This runbook is intentionally operational and conservative: it records state, backs up config/data, then runs read-only smoke checks before and after any change.

Do not paste secret values into tickets, PRs, Telegram, or logs. When a command can print env, tokens, OAuth files, SSH keys, or service credentials, capture only metadata such as path, mode, size, owner, and redacted key names.

## When to Use This

Run this before any change that touches:

- `agent/`, `tools/`, `gateway/`, `cron/`, `hermes_cli/`, `igor-os/skills/`, or `~/.hermes` runtime config.
- Tool permissions, confirmation gates, memory providers, web ingestion, code execution, Telegram, Google access, Docker, or systemd units.
- Any change that may require restarting `hermes-gateway.service` or `hindsight`.

## Pre-Change Backup

Set a timestamp and create a backup root:

```bash
cd ~/hermes-agent
TS=$(date -u +%Y%m%dT%H%M%SZ)
BACKUP_DIR="$HOME/hermes-backups/pre-change-$TS"
mkdir -p "$BACKUP_DIR"/{repo,config,state,deployment,logs}
```

Record repository state without staging unrelated files:

```bash
git status --short --branch > "$BACKUP_DIR/repo/git-status.txt"
git rev-parse HEAD > "$BACKUP_DIR/repo/git-head.txt"
git diff > "$BACKUP_DIR/repo/tracked.diff"
git ls-files --others --exclude-standard -z \
  | tar --null -T - -czf "$BACKUP_DIR/repo/untracked.tar.gz" \
  2> "$BACKUP_DIR/repo/untracked-tar.stderr" || true
git branch "backup/pre-change-$TS" HEAD
```

Back up runtime config while preserving permissions:

```bash
cp -a ~/.config/systemd/user/hermes-gateway.service "$BACKUP_DIR/config/" 2>/dev/null || true
cp -a ~/.hermes/config.yaml ~/.hermes/.env ~/.hermes/auth.json "$BACKUP_DIR/config/" 2>/dev/null || true
cp -a ~/.hermes/google_token.json ~/.hermes/google_client_secret.json "$BACKUP_DIR/config/" 2>/dev/null || true
mkdir -p "$BACKUP_DIR/config/cron"
cp -a ~/.hermes/cron/jobs.json "$BACKUP_DIR/config/cron/" 2>/dev/null || true
cp -a docker-compose.yml Dockerfile "$BACKUP_DIR/config/" 2>/dev/null || true
```

Back up local state and memory:

```bash
cp -a ~/.hermes/memories "$BACKUP_DIR/state/" 2>/dev/null || true
cp -a ~/.hermes/state.db ~/.hermes/state.db-shm ~/.hermes/state.db-wal "$BACKUP_DIR/state/" 2>/dev/null || true
cp -a ~/.hermes/kanban.db ~/.hermes/kanban.db-shm ~/.hermes/kanban.db-wal "$BACKUP_DIR/state/" 2>/dev/null || true
cp -a ~/.hindsight "$BACKUP_DIR/state/hindsight" 2>/dev/null || true
```

Record deployment inventory without exposing secrets:

```bash
systemctl --user show hermes-gateway.service --no-pager > "$BACKUP_DIR/deployment/hermes-gateway.show.txt" 2>&1 || true
systemctl --user cat hermes-gateway.service > "$BACKUP_DIR/deployment/hermes-gateway.unit.txt" 2>&1 || true
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' > "$BACKUP_DIR/deployment/docker-ps.txt" 2>&1 || true
docker inspect hindsight \
  --format 'Name={{.Name}} Image={{.Config.Image}} User={{.Config.User}} NetworkMode={{.HostConfig.NetworkMode}} Restart={{.HostConfig.RestartPolicy.Name}} Mounts={{range .Mounts}}{{.Source}}->{{.Destination}}({{.RW}}) {{end}}' \
  > "$BACKUP_DIR/deployment/hindsight-inspect-summary.txt" 2>&1 || true
ss -ltnup > "$BACKUP_DIR/deployment/ports.txt" 2>&1 || true
crontab -l > "$BACKUP_DIR/deployment/crontab.txt" 2>&1 || true
systemctl --user list-timers --all --no-pager > "$BACKUP_DIR/deployment/user-timers.txt" 2>&1 || true
```

Optional metadata-only secret inventory:

```bash
for f in ~/.hermes/.env ~/.hermes/auth.json ~/.hermes/google_token.json ~/.hermes/google_client_secret.json; do
  [ -f "$f" ] && stat -c '%n mode=%A owner=%U group=%G size=%s mtime=%y' "$f"
done > "$BACKUP_DIR/config/secret-file-metadata.txt"
```

## Pre-Change Smoke Checks

Run only read-only checks unless the change explicitly requires a write-path test.

Service health:

```bash
systemctl --user is-active hermes-gateway.service
systemctl --user status hermes-gateway.service --no-pager | sed -n '1,40p'
```

Repository and Python test baseline:

```bash
git status --short --branch
./venv/bin/python -m pytest tests/agent/test_tool_risk_registry.py tests/agent/test_tool_guardrails.py -q
```

Runtime read-only checks:

```bash
curl -fsS http://127.0.0.1:8888/ >/dev/null || true
journalctl --user -u hermes-gateway.service -n 80 --no-pager \
  | sed -E 's#(Bearer )[A-Za-z0-9._~+/-]+#\1[REDACTED]#g; s#(TOKEN|SECRET|KEY|PASSWORD|PASS|AUTH|CREDENTIAL|CLIENT)[A-Za-z0-9_]*[=:][^[:space:]]+#\1=[REDACTED]#Ig' \
  > "$BACKUP_DIR/logs/hermes-journal-tail-redacted.txt"
```

Manual smoke checks to record in the PR or deployment notes:

- Send one Telegram DM from an allowlisted user and confirm a normal response.
- Run a harmless Google Calendar list/read check if the change touches Google access.
- Run a harmless memory read if the change touches memory.
- Run a safe web search/extract only if the change touches web ingestion.

## Change Gate

Do not deploy or restart services unless all are true:

- Backup directory exists and contains repo, config, state, and deployment inventory.
- The intended diff is reviewed and excludes unrelated dirty files.
- Targeted tests pass.
- Manual rollback commands below are still valid for this host.
- The user explicitly approves any service restart, credential rotation, firewall change, Docker change, or production write test.

## Rollback

Rollback should be chosen quickly if post-change smoke tests fail or logs show secret leakage, repeated crashes, blocked Telegram responses, broken memory, or broken Google access.

Repository rollback:

```bash
cd ~/hermes-agent
git status --short --branch
git switch <previous-branch>
git reset --hard <known-good-commit>
tar -xzf "$BACKUP_DIR/repo/untracked.tar.gz" -C ~/hermes-agent 2>/dev/null || true
git apply "$BACKUP_DIR/repo/tracked.diff" 2>/dev/null || true
```

Config rollback, only after user approval because it may require restart:

```bash
cp -a "$BACKUP_DIR/config/hermes-gateway.service" ~/.config/systemd/user/hermes-gateway.service
cp -a "$BACKUP_DIR/config/config.yaml" ~/.hermes/config.yaml
cp -a "$BACKUP_DIR/config/.env" ~/.hermes/.env
cp -a "$BACKUP_DIR/config/auth.json" ~/.hermes/auth.json
cp -a "$BACKUP_DIR/config/cron/jobs.json" ~/.hermes/cron/jobs.json 2>/dev/null || true
systemctl --user daemon-reload
systemctl --user restart hermes-gateway.service
```

State rollback, only after user approval and after stopping dependent services:

```bash
systemctl --user stop hermes-gateway.service
cp -a "$BACKUP_DIR/state/memories" ~/.hermes/memories
cp -a "$BACKUP_DIR/state"/state.db* ~/.hermes/ 2>/dev/null || true
cp -a "$BACKUP_DIR/state"/kanban.db* ~/.hermes/ 2>/dev/null || true
systemctl --user start hermes-gateway.service
```

Hindsight rollback requires an explicit service/container procedure. Do not overwrite `~/.hindsight` while the container is running unless a Hindsight-specific restore path has been verified.

## Post-Change Verification

After a change or rollback:

```bash
systemctl --user is-active hermes-gateway.service
journalctl --user -u hermes-gateway.service -n 120 --no-pager \
  | sed -E 's#(Bearer )[A-Za-z0-9._~+/-]+#\1[REDACTED]#g; s#(TOKEN|SECRET|KEY|PASSWORD|PASS|AUTH|CREDENTIAL|CLIENT)[A-Za-z0-9_]*[=:][^[:space:]]+#\1=[REDACTED]#Ig' \
  | sed -n '1,160p'
```

Confirm the same manual smoke checks used before the change. If any fail, rollback first and investigate second.
