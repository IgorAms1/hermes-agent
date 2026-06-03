# Session File Parsing

Reliable technique for extracting user messages from Hermes session files.

Hermes stores sessions in two complementary formats — prefer the **`.json` full dump** for completeness and simplicity, fall back to `.jsonl` for incremental context.

## Location

Session files live at `~/.hermes/sessions/` with two naming patterns:

| Format | Pattern | Content |
|--------|---------|---------|
| **`.json` (preferred)** | `session_YYYYMMDD_HHMMSS_<id>.json` | Full session dump — single JSON object with all messages, timestamps, and metadata. One file per checkpoint. Can be large (1000s of lines), but complete. |
| **`.jsonl`** | `YYYYMMDD_HHMMSS_<id>.jsonl` | Incremental log — one JSON object per line. Useful for streaming/real-time but may lack later messages present in json dumps. |

## File Format

Each line in `.jsonl` is a JSON object with `role`, `content`, `timestamp`, etc.
Each `.json` file is a single JSON object with a `"messages"` array containing all messages.

Voice messages have transcription in the `content` field: `[The user sent a voice message~ Here's what they said: "..."]`.

## Reading via `read_file` (for `.jsonl` only)

The `read_file` tool returns lines with line-number prefixes:

```
     1|{"role": "session_meta", ...}
     2|{"role": "user", "content": "...", "timestamp": "..."}
```

Extraction pattern:

```python
import json, re
from hermes_tools import read_file

result = read_file(session_path, limit=200)
text = result['content']

user_msgs = []
for raw_line in text.split('\n'):
    raw_line = raw_line.strip()
    if not raw_line:
        continue
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

## Reading via `terminal` + `python -c` (for `.json` — recommended for large files)

For `.json` full dumps (often 5000+ lines), `read_file` truncates at ~100K chars. Use `terminal` with Python directly instead:

```bash
cd ~/.hermes/sessions && python3 -c "
import json
with open('session_YYYYMMDD_HHMMSS_<id>.json') as f:
    data = json.load(f)
msgs = [m for m in data.get('messages', []) if m.get('role') == 'user']
for i, m in enumerate(msgs):
    ts = m.get('timestamp', '?')
    c = str(m.get('content', ''))[:300].replace('\n', ' | ')
    print(f'[{i}] {ts} | {c}')
"
```

This approach:
- Has no file-size limit (unlike `read_file`)
- Preserves JSON structure (no regex parsing needed)
- Lets you filter/transform inline

### ⚠️ Quoting trap when called from `execute_code`

The inline `python3 -c "..."` pattern above works from a bare `terminal()` call, but **breaks when called from inside `execute_code`**. Nested Python string escaping (double quotes inside the `terminal()` call argument) causes syntax errors:

```python
# THIS FAILS — nested quoting:
from hermes_tools import terminal
result = terminal("python3 -c \"import json\n...\"")  # syntax error in execute_code
```

**Fix:** Write a standalone Python script file via `write_file`, then invoke it with `terminal()`:

```python
# THIS WORKS — script file + terminal:
from hermes_tools import write_file, terminal

write_file(path='/tmp/extract_session.py', content='''
import json
with open('session_YYYYMMDD_HHMMSS.json') as f:
    data = json.load(f)
msgs = [m for m in data.get('messages', []) if m.get('role') == 'user']
for m in msgs:
    print(m.get('content', '')[:300])
''')

result = terminal('python3 /tmp/extract_session.py')
```

The script-file approach:
- Eliminates all quoting issues (no nested escaping)
- Makes the code debuggable (you can `read_file` the script)
- Works for any multi-line Python from `execute_code` (Hindsight recall, calendar reads, session parsing)

## Finding Today's Sessions

```bash
ls -lt ~/.hermes/sessions/ | grep "$(date +%Y%m%d)"
```

This lists both `.jsonl` and `.json` files sorted by modification time. The largest `.json` file is usually the most complete checkpoint for the day.

## Voice Message Content

Voice transcriptions are prefixed: `[The user sent a voice message~ Here's what they said: "TRANSCRIPTION"]`. Extract the quoted text between the innermost double quotes. Important details are often buried here and invisible in `session_search` summaries.

## Why Not delegate_task

`delegate_task` with `toolsets: ["terminal", "file"]` can time out at 600s when crawling multiple session files, even with only 1 API call completed. The direct `execute_code` + `read_file` approach is faster and deterministic.
