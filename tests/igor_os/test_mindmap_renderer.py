import json
import importlib.util
import subprocess
import sys
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[2]
RENDERER = REPO_ROOT / "igor-os" / "scripts" / "render_mindmap.py"


def _load_renderer_module():
    spec = importlib.util.spec_from_file_location("render_mindmap", RENDERER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_renderer_uses_real_ttf_font_for_cyrillic():
    module = _load_renderer_module()

    regular = Path(module._font_path(False))
    bold = Path(module._font_path(True))

    assert regular.exists()
    assert bold.exists()
    assert "DejaVuSans" in regular.name
    assert "DejaVuSans" in bold.name


def test_render_mindmap_flow_png_with_cyrillic(tmp_path):
    spec = {
        "title": "Процесс deep research",
        "subtitle": "Короткая схема для Telegram",
        "layout": "flow",
        "palette": "ocean",
        "nodes": [
            {
                "title": "1. Уточнить задачу",
                "body": "Сформулировать решение, аудиторию и критерии успеха.",
                "items": ["Не больше трех вопросов", "Если контекста хватает - стартовать"],
            },
            {
                "title": "2. Разбить на потоки",
                "body": "Запустить независимые ветки исследования и собрать источники.",
            },
            {
                "title": "3. Синтезировать вывод",
                "body": "Сжать результат в решение, риски и следующие действия.",
            },
        ],
        "footer": "Тестовый PNG",
    }
    spec_path = tmp_path / "mindmap.json"
    out_path = tmp_path / "mindmap.png"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(RENDERER), str(spec_path), str(out_path)],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "OK" in result.stdout
    assert out_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert out_path.stat().st_size > 10_000
    with Image.open(out_path) as img:
        assert img.format == "PNG"
        assert img.width >= 1200
        assert img.height >= 700
