# Igor OS Security And Privacy

- Never print, request, or store secrets in chat.
- Never commit `.env`, logs, local memory databases, private notes, or API tokens.
- Telegram must use an allowlist through `TELEGRAM_ALLOWED_USERS`.
- Do not set `GATEWAY_ALLOW_ALL_USERS=true` for Igor OS.
- Warn before connecting Gmail, calendar, company systems, private repositories, or shared drives.
- Keep work-sensitive information in local/private context files only.
- Use least-privilege users on a VPS.
- Prefer long polling before webhook mode unless HTTPS and exposure are understood.
- If a request might expose company confidential information, ask for a sanitized version or keep the answer high-level.
