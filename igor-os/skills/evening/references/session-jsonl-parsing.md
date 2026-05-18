# Session JSONL Parsing

Reliable technique for extracting user messages from Hermes session files.

## Location

Session files live at `~/.hermes/sessions/` with names like `YYYYMMDD_HHMMSS_sessionid.jsonl`.

## File Format

Each line is a JSON object with `role`, `content`, `timestamp`, etc. Voice messages have transcription in the `content` field prefixed with `[The user sent a voice message~ Here's what they said: "..."]`.

## Reading via `read_file`

The `read_file` tool returns lines with line-number prefixes:

```
     1|{"role": "session_meta", ...}
     2|{"role": "user", "content": "...", "timestamp": "..."}
```

## Extraction Pattern (execute_code)

```python
import json, re
from hermes_tools import read_file

result = read_file(session_path, limit=200)  # limit per call to avoid truncation
text = result['content']

user_msgs = []
for raw_line in text.split('\n'):
    raw_line = raw_line.strip()
    if not raw_line:
        continue
    # Strip "    N|" prefix
    m = re.match(r'\s*\d+\|(.+)', raw_line)
    if not m:
        continue
    try:
        msg = json.loads(m.group(1))
    except json.JSONDecodeError:
        continue
    if msg.get('role') == 'user':
        user_msgs.append({
            'timestamp': msg.get('timestamp', ''),
            'content': msg.get('content', ''),
        })
```

## Finding Today's Sessions

```bash
ls ~/.hermes/sessions/$(date +%Y%m%d)*.jsonl
```

Then read each matching file, extract user messages, and filter for completions / cancellations / new tasks / corrections.

## Voice Message Content

Voice transcriptions are prefixed: `[The user sent a voice message~ Here's what they said: "TRANSCRIPTION"]`. Extract the quoted text between the innermost double quotes. Important details are often buried here and invisible in `session_search` summaries.

## Why Not delegate_task

`delegate_task` with `toolsets: ["terminal", "file"]` can time out at 600s when crawling multiple session files, even with only 1 API call completed. The direct `execute_code` + `read_file` approach is faster and deterministic.
