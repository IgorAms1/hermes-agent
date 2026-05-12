# Igor OS for Hermes Agent

Igor OS is an additive personal operating layer for Hermes Agent. It does not replace Hermes internals. It uses Hermes' existing OpenRouter provider, Telegram gateway, context files, skills, memory, and cron scheduler.

## File Tree

```text
igor-os/
  .env.example
  .hermes.md
  config/
    cli-config.igor-os.yaml
  context/
    personal-profile.example.md
    memory-policy.md
    security-and-privacy.md
  cron/
    examples.md
  scripts/
    install-igor-os.sh
  skills/
    morning/SKILL.md
    evening/SKILL.md
    work/SKILL.md
    research/SKILL.md
    dutch/SKILL.md
    fishing/SKILL.md
    training/SKILL.md
    relationship/SKILL.md
    weekly/SKILL.md
    decision/SKILL.md
    avoidance/SKILL.md
    briefing_pack/SKILL.md
    buying_decision/SKILL.md
    field_note/SKILL.md
    after_action/SKILL.md
    energy/SKILL.md
    dutch_real_life/SKILL.md
  workflows/
    telegram-commands.md
    first-7-days.md
```

## Setup: Local macOS

1. Install Hermes dependencies from the repo root:

   ```bash
   ./setup-hermes.sh
   ```

2. Install the Igor OS config and skill directory references:

   ```bash
   ./igor-os/scripts/install-igor-os.sh
   ```

3. Copy the env example and fill in real values:

   ```bash
   cp igor-os/.env.example ~/.hermes/.env
   chmod 600 ~/.hermes/.env
   ```

4. Edit `~/.hermes/.env`:

   - `OPENROUTER_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_ALLOWED_USERS`
   - optionally `TELEGRAM_HOME_CHANNEL`

5. Start the gateway from the Igor OS directory so `.hermes.md` is loaded:

   ```bash
   cd igor-os
   hermes gateway
   ```

6. In Telegram, message your bot:

   ```text
   /help
   /morning
   /evening
   /work messy notes from a partner call...
   /research compare pike fishing methods for Amsterdam canals
   /dutch correct: Ik heb gisteren naar kantoor gefietst
   /fishing log tonight's session...
   /training BJJ session notes...
   /relationship suggest something small for tonight
   /weekly
   /decision should I switch models?
   /avoidance I keep avoiding the partner follow-up
   /briefing_pack prep tomorrow's partner call
   /buying_decision should I buy this fishing rod?
   /field_note heard "komt goed" at the gym
   /after_action review today's interview
   /energy slept badly and have four meetings
   /dutch_real_life making a dentist appointment
   ```

## OpenRouter

Igor OS sets OpenRouter as the default provider in `igor-os/config/cli-config.igor-os.yaml`.

The default model is:

```yaml
model:
  provider: "openrouter"
  default: "anthropic/claude-opus-4.6"
```

Change the model by setting `HERMES_INFERENCE_MODEL` in `~/.hermes/.env` or by editing the config after install. Keep `OPENROUTER_API_KEY` only in `.env`.

## Telegram

Create a bot:

1. Open Telegram and message `@BotFather`.
2. Send `/newbot`.
3. Choose a display name and username.
4. Copy the bot token into `TELEGRAM_BOT_TOKEN`.

Find your Telegram user ID:

1. Message `@userinfobot` or `@RawDataBot`.
2. Copy your numeric ID into `TELEGRAM_ALLOWED_USERS`.
3. If you use cron delivery, set `TELEGRAM_HOME_CHANNEL` to your chat ID. You can set it from Telegram with Hermes' `/sethome` command after the gateway is running.

Security note: `TELEGRAM_ALLOWED_USERS` is required. Do not set `GATEWAY_ALLOW_ALL_USERS=true` for Igor OS.

## Scheduled Reviews

Cron jobs are managed by Hermes, not custom Igor OS code. See `igor-os/cron/examples.md`.

Typical setup:

```bash
hermes cron create "0 7 * * *" "Create today's Igor OS morning brief." --skill morning --deliver telegram --workdir "$(pwd)/igor-os" --name "Igor OS Morning Brief"
hermes cron create "0 21 * * *" "Run evening capture. Ask the capture questions and wait for my reply if needed." --skill evening --deliver telegram --workdir "$(pwd)/igor-os" --name "Igor OS Evening Capture"
hermes cron create "0 10 * * 0" "Create the Igor OS weekly review." --skill weekly --deliver telegram --workdir "$(pwd)/igor-os" --name "Igor OS Weekly Review"
```

The gateway must be running for cron jobs to fire.

## VPS Notes

Use a least-privilege Linux user, for example `hermes`, and keep secrets in `~/.hermes/.env` with `chmod 600`.

Basic deployment shape:

```bash
sudo adduser --disabled-password --gecos "" hermes
sudo su - hermes
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh
./igor-os/scripts/install-igor-os.sh
cp igor-os/.env.example ~/.hermes/.env
chmod 600 ~/.hermes/.env
```

Then edit `~/.hermes/.env`, start the gateway once, confirm Telegram works, and install the gateway as a user service:

```bash
cd ~/hermes-agent/igor-os
hermes gateway
hermes gateway install
hermes cron status
```

Prefer long polling for a simple VPS. Use Telegram webhook mode only if you already operate HTTPS and understand the exposure.

## Security And Privacy

- Never commit `.env`, logs, local memory stores, or copied private notes.
- Never paste API keys or passwords into Telegram.
- Keep `TELEGRAM_ALLOWED_USERS` set to your numeric user ID.
- Warn before connecting Gmail, calendar, company systems, private repos, or shared drives.
- Keep work-sensitive information in local/private context files only.
- Do not store company confidential data as durable memory.
- Use a separate VPS user and avoid running the agent as root.

## Local Test Steps

1. `hermes doctor`
2. `hermes chat --config igor-os/config/cli-config.igor-os.yaml --toolsets skills -q "/morning"`
3. `cd igor-os && hermes gateway`
4. Send `/help` and `/morning` to the Telegram bot.
5. Create a test cron job:

   ```bash
   hermes cron create "once in 2m" "Send a short Igor OS cron test." --skill morning --deliver telegram --workdir "$(pwd)/igor-os" --name "Igor OS Cron Test"
   ```

6. Confirm only your allowed Telegram user can interact with the bot.

## First Seven Days

See `igor-os/workflows/first-7-days.md`.
