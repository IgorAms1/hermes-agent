# Google Calendar Integration — Actual State

## Status: ACTIVE (connected 22-23 May 2026)

Token exists at `~/.hermes/google_token.json` — NOT `google_calendar_token.json`.

## Token Details

- **File:** `~/.hermes/google_token.json`
- **Client secret:** `~/.hermes/google_client_secret.json`
- **Scopes:** calendar (read+write), docs, sheets, gmail (read+send), drive, contacts
- **Refresh token:** Present, auto-refresh works
- **Account:** igor.kluchnikov@gmail.com (personal primary)

## How to Read Calendar (Working Method)

There is no standalone CLI script. Use direct Python from the Hermes venv:

```python
import json, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = os.path.expanduser('~/.hermes/google_token.json')
creds = Credentials.from_authorized_user_file(token_path)
service = build('calendar', 'v3', credentials=creds)

# Today's events
now = '2026-05-24T00:00:00+02:00'
end = '2026-05-25T00:00:00+02:00'
events = service.events().list(
    calendarId='primary',
    timeMin=now, timeMax=end,
    singleEvents=True, orderBy='startTime'
).execute()
```

Write to a temp file like `/tmp/check_calendar.py`, then run:
```bash
cd /home/igor1/hermes-agent && source venv/bin/activate && python3 /tmp/check_calendar.py
```

## Multi-Account

Currently only igor.kluchnikov@gmail.com is connected (as 'primary' calendarId).
igor@semaphoreui.com (work) would need a separate OAuth flow and a second token file.

To add a second account, run a fresh OAuth flow with a different client secret or the same one with account switching.

## Morning Brief Integration

Insert a `📅 Сегодня в календаре` section after work priorities. If no events, show "Событий нет".

## Token Expiry / Re-auth Workflow

The OAuth token can expire or be revoked (error: `invalid_grant: Token has been expired or revoked`). The setup script detects this:

```
$ python $HERMES_HOME/skills/productivity/google-workspace/scripts/setup.py --check
TOKEN_REVOKED: ('invalid_grant: ...')
```

### Full re-auth procedure:

1. **Clean stale state:**
   ```bash
   rm -f ~/.hermes/google_oauth_pending.json ~/.hermes/google_token.json
   ```

2. **Generate auth URL:**
   ```bash
   python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-url
   ```

3. **Send URL to user** — user opens in browser, grants permissions, copies the redirect URL (`http://localhost:1/?state=...&code=...`)

4. **Exchange code:**
   ```bash
   python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-code "http://localhost:1/?code=..."
   ```

5. **Verify:**
   ```bash
   python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check
   # Should print AUTHENTICATED
   ```

### Known limitation: setup.py PKCE fails (workaround)

### Known limitation: setup.py PKCE fails (workaround)

The `setup.py` always uses PKCE (`code_challenge_method=S256`). For this OAuth client configuration, Google can reject PKCE during token exchange with: `invalid_grant: code_verifier or verifier is not needed`.

If the standard re-auth fails with this error **even after cleaning pending and starting fresh**, use the manual no-PKCE flow below.

#### Manual URL generation (without PKCE)

Important: load the client secret once; do not call `json.load(f)` twice on the same file handle.

```python
import secrets, json, os
from pathlib import Path
from urllib.parse import urlencode

HERMES_HOME = Path(os.path.expanduser('~/.hermes'))

with open(HERMES_HOME / 'google_client_secret.json') as f:
    raw = json.load(f)
cs = raw.get('installed') or raw.get('web')

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
]

state = secrets.token_urlsafe(16)
params = {
    'response_type': 'code',
    'client_id': cs['client_id'],
    'redirect_uri': 'http://localhost:1',
    'scope': ' '.join(SCOPES),
    'state': state,
    'access_type': 'offline',
    'prompt': 'consent',
    # Intentionally no code_challenge / code_challenge_method
}
auth_url = 'https://accounts.google.com/o/oauth2/auth?' + urlencode(params)

pending = {'state': state, 'redirect_uri': 'http://localhost:1', 'no_pkce': True}
(HERMES_HOME / 'google_oauth_pending.json').write_text(json.dumps(pending, indent=2))
print(auth_url)
```

#### Manual token exchange (without PKCE)

Accept the full redirect URL from Igor, verify `state`, extract `code` and `scope`, then write the token. Preserve the old refresh token only if Google does not return a new one.

```python
import json, os, requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs

callback = '<full http://localhost:1/?state=...&code=... URL from Igor>'
HERMES_HOME = Path(os.path.expanduser('~/.hermes'))
pending_path = HERMES_HOME / 'google_oauth_pending.json'
secret_path = HERMES_HOME / 'google_client_secret.json'
token_path = HERMES_HOME / 'google_token.json'

pending = json.loads(pending_path.read_text())
params = parse_qs(urlparse(callback).query)
code = params.get('code', [''])[0]
state = params.get('state', [''])[0]
if not code:
    raise SystemExit('no code in callback')
if state != pending.get('state'):
    raise SystemExit('state mismatch')

with secret_path.open() as f:
    raw = json.load(f)
cs = raw.get('installed') or raw.get('web')

data = {
    'code': code,
    'client_id': cs['client_id'],
    'client_secret': cs.get('client_secret'),
    'redirect_uri': pending.get('redirect_uri', 'http://localhost:1'),
    'grant_type': 'authorization_code',
}
r = requests.post('https://oauth2.googleapis.com/token', data=data, timeout=30)
r.raise_for_status()
token = r.json()
granted_scopes = (params.get('scope', [''])[0] or token.get('scope', '')).split()

token_payload = {
    'token': token['access_token'],
    'refresh_token': token.get('refresh_token'),
    'token_uri': 'https://oauth2.googleapis.com/token',
    'client_id': cs['client_id'],
    'client_secret': cs.get('client_secret'),
    'scopes': granted_scopes,
    'expiry': None,
    'account': '',
    'type': 'authorized_user',
}
if not token_payload['refresh_token'] and token_path.exists():
    old = json.loads(token_path.read_text())
    token_payload['refresh_token'] = old.get('refresh_token')

token_path.write_text(json.dumps(token_payload, indent=2))
pending_path.unlink(missing_ok=True)
print('EXCHANGE_OK')
```

After exchange, run `setup.py --check-live` and then a real calendar read (`google_api.py calendar list`) to verify integration end-to-end.

**Important:** remind Igor to select ALL scopes in the consent screen, not just Calendar — otherwise gmail/drive/docs features will be unavailable without re-auth.

## Security

- Tokens stored locally, never transmitted
- Read-write access to calendar, drive, gmail — be careful with write operations
- Revokable at https://myaccount.google.com/permissions
