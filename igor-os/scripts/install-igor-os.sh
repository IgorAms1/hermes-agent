#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IGOR_OS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
CONFIG_FILE="${HERMES_HOME}/config.yaml"

mkdir -p "${HERMES_HOME}"

if [ ! -f "${CONFIG_FILE}" ]; then
  cp "${IGOR_OS_DIR}/config/cli-config.igor-os.yaml" "${CONFIG_FILE}"
else
  BACKUP="${CONFIG_FILE}.before-igor-os.$(date +%Y%m%d%H%M%S)"
  cp "${CONFIG_FILE}" "${BACKUP}"
  python3 - "$CONFIG_FILE" "$IGOR_OS_DIR" <<'PY'
from pathlib import Path
import sys

config_path = Path(sys.argv[1])
igor_dir = Path(sys.argv[2]).resolve()
text = config_path.read_text(encoding="utf-8")

if "provider: \"openrouter\"" not in text and "provider: 'openrouter'" not in text:
    text += "\n\n# Igor OS default provider\nmodel:\n  provider: \"openrouter\"\n  default: \"anthropic/claude-opus-4.6\"\n  base_url: \"https://openrouter.ai/api/v1\"\n"

external_block = f"    - \"{igor_dir}/skills\""
if str(igor_dir / "skills") not in text:
    if "skills:" not in text:
        text += f"\n\nskills:\n  external_dirs:\n{external_block}\n"
    elif "external_dirs:" not in text:
        text += f"\n\n# Igor OS external skills\nskills:\n  external_dirs:\n{external_block}\n"
    else:
        text += f"\n# Igor OS external skills\n{external_block}\n"

config_path.write_text(text, encoding="utf-8")
PY
  echo "Backed up existing config to ${BACKUP}"
fi

ENV_FILE="${HERMES_HOME}/.env"
if [ ! -f "${ENV_FILE}" ]; then
  cp "${IGOR_OS_DIR}/.env.example" "${ENV_FILE}"
  chmod 600 "${ENV_FILE}"
fi

if ! grep -q '^IGOR_OS_DIR=' "${ENV_FILE}" 2>/dev/null; then
  {
    echo ""
    echo "# Igor OS directory"
    echo "IGOR_OS_DIR=${IGOR_OS_DIR}"
    echo "MESSAGING_CWD=${IGOR_OS_DIR}"
  } >> "${ENV_FILE}"
fi

if ! grep -q '^HERMES_INFERENCE_PROVIDER=' "${ENV_FILE}" 2>/dev/null; then
  echo "HERMES_INFERENCE_PROVIDER=openrouter" >> "${ENV_FILE}"
fi

if ! grep -q '^HERMES_INFERENCE_MODEL=' "${ENV_FILE}" 2>/dev/null; then
  echo "HERMES_INFERENCE_MODEL=anthropic/claude-opus-4.6" >> "${ENV_FILE}"
fi

echo "Igor OS installed."
echo "Config: ${CONFIG_FILE}"
echo "Env:    ${ENV_FILE}"
echo "Next: fill OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN, and TELEGRAM_ALLOWED_USERS in ${ENV_FILE}"
