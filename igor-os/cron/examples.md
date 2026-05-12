# Igor OS Cron Examples

Run these from the Hermes repo root after `./igor-os/scripts/install-igor-os.sh`.

Replace the schedule times if needed. The cron expressions below use the server's local timezone.

```bash
IGOR_OS_WORKDIR="$(pwd)/igor-os"
```

## Morning Brief

```bash
hermes cron create "0 7 * * *" \
  "Create today's Igor OS morning brief. Use current date, available memory/context, and any known priorities." \
  --skill morning \
  --deliver telegram \
  --workdir "$IGOR_OS_WORKDIR" \
  --name "Igor OS Morning Brief"
```

## Evening Capture

```bash
hermes cron create "0 21 * * *" \
  "Start evening capture. Ask the capture questions clearly and wait for Igor's answers if needed." \
  --skill evening \
  --deliver telegram \
  --workdir "$IGOR_OS_WORKDIR" \
  --name "Igor OS Evening Capture"
```

## Weekly Review

```bash
hermes cron create "0 10 * * 0" \
  "Create the Igor OS weekly review using available logs, memory, and context." \
  --skill weekly \
  --deliver telegram \
  --workdir "$IGOR_OS_WORKDIR" \
  --name "Igor OS Weekly Review"
```

## Management

```bash
hermes cron list
hermes cron status
hermes cron pause <job_id>
hermes cron resume <job_id>
hermes cron run <job_id>
hermes cron remove <job_id>
```
