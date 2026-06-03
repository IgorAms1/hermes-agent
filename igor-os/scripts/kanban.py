#!/usr/bin/env python3
"""Telegram kanban command — /kanban view|add|done|move."""
import sys, os

os.environ.setdefault("HERMES_HOME", os.path.expanduser("~/.hermes"))
sys.path.insert(0, os.path.expanduser("~/hermes-agent"))

from hermes_cli import kanban_db
from datetime import datetime, timezone, timedelta

AMSTERDAM = timezone(timedelta(hours=2))  # CEST

STATUS_EMOJI = {
    "triage": "🔍",
    "todo": "📋",
    "ready": "🟢",
    "running": "🔄",
    "blocked": "🔴",
    "done": "✅",
}
STATUS_ORDER = ["todo", "ready", "running", "blocked", "done"]


def now_amsterdam():
    return datetime.now(AMSTERDAM)


def view_board():
    conn = kanban_db.connect()
    kanban_db.init_db()
    tasks = kanban_db.list_tasks(conn, include_archived=False)
    conn.close()

    today = now_amsterdam().strftime("%Y-%m-%d")

    by_status = {}
    for t in tasks:
        by_status.setdefault(t.status, []).append(t)

    if not tasks:
        return "📋 Kanban — чисто. Нет задач."

    lines = [f"📋 Kanban — {len(tasks)} задач\n"]

    # Show today's done items first
    done_today = [
        t
        for t in by_status.get("done", [])
        if t.completed_at
        and datetime.fromtimestamp(t.completed_at, tz=AMSTERDAM).strftime("%Y-%m-%d") == today
    ]
    if done_today:
        lines.append("✅ Сделано сегодня:")
        for t in done_today:
            lines.append(f"  {t.id[:6]} — {t.title}")
        lines.append("")

    # Open items grouped (skip empty sections)
    for status in STATUS_ORDER:
        ts = by_status.get(status, [])
        if not ts:
            continue
        # For "done" section, only show non-today items
        if status == "done":
            prev_done = [t for t in ts if not (t.completed_at and datetime.fromtimestamp(t.completed_at, tz=AMSTERDAM).strftime("%Y-%m-%d") == today)]
            if not prev_done:
                continue
            emoji = "✅"
            lines.append(f"{emoji} Ранее:")
            for t in prev_done:
                lines.append(f"  └ {t.id[:6]} — {t.title}")
            lines.append("")
            continue

        emoji = STATUS_EMOJI.get(status, "📌")
        label = {"todo": "К выполнению", "ready": "Готово", "running": "В работе", "blocked": "Заблокировано"}[status]
        lines.append(f"{emoji} {label}:")
        for t in ts:
            lines.append(f"  └ {t.id[:6]} — {t.title}")
        lines.append("")

    return "\n".join(lines).strip()


def add_task(title):
    if not title or not title.strip():
        return "❌ Напиши название задачи: `/kanban add купить корм`"

    conn = kanban_db.connect()
    kanban_db.init_db()
    task_id = kanban_db.create_task(conn, title=title.strip(), created_by="igor")
    conn.close()
    return f"✅ Добавлено: `{task_id[:6]}` — {title.strip()}"


def done_task(task_id_prefix):
    conn = kanban_db.connect()
    kanban_db.init_db()

    # Find by prefix
    tasks = kanban_db.list_tasks(conn, include_archived=False)
    match = [t for t in tasks if t.id.startswith(task_id_prefix)]
    conn.close()

    if not match:
        return f"❌ Задача `{task_id_prefix}` не найдена"
    if len(match) > 1:
        ids = ", ".join(t.id[:6] for t in match)
        return f"❌ Найдено несколько: {ids}. Уточни id."

    task = match[0]
    conn = kanban_db.connect()
    kanban_db.complete_task(conn, task.id, result="done")
    conn.close()
    return f"✅ Выполнено: {task.title}"


def move_task(task_id_prefix, new_status):
    valid = kanban_db.VALID_STATUSES
    if new_status not in valid:
        return f"❌ Статус должен быть один из: {', '.join(sorted(valid))}"

    conn = kanban_db.connect()
    kanban_db.init_db()

    tasks = kanban_db.list_tasks(conn, include_archived=False)
    match = [t for t in tasks if t.id.startswith(task_id_prefix)]
    if not match:
        conn.close()
        return f"❌ Задача `{task_id_prefix}` не найдена"
    if len(match) > 1:
        ids = ", ".join(t.id[:6] for t in match)
        conn.close()
        return f"❌ Найдено несколько: {ids}. Уточни id."

    task = match[0]
    conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task.id))
    conn.commit()
    conn.close()
    return f"✅ {task.title[:40]} → {new_status}"


def main():
    if len(sys.argv) < 2:
        print(view_board())
        return

    cmd = sys.argv[1]

    if cmd == "list" or cmd == "show" or cmd == "view":
        print(view_board())
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("❌ Напиши название: /kanban add <название>")
        else:
            print(add_task(" ".join(sys.argv[2:])))
    elif cmd == "done" or cmd == "complete" or cmd == "finish":
        if len(sys.argv) < 3:
            print("❌ Укажи id: /kanban done <id>")
        else:
            print(done_task(sys.argv[2]))
    elif cmd == "move":
        if len(sys.argv) < 4:
            print("❌ Укажи id и статус: /kanban move <id> <status>")
        else:
            print(move_task(sys.argv[2], sys.argv[3]))
    else:
        print(f"❌ Неизвестная команда: {cmd}. Доступно: list, add, done, move")


if __name__ == "__main__":
    main()
