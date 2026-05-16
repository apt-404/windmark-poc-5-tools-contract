#!/usr/bin/env python3
"""
run-agent-loop.py — Orquestador agéntico

Uso:
  python run-agent-loop.py [--max-iter N] [--max-retries N]

Comportamiento: AFK por tarea dentro de cada feature; HITL al terminar cada feature.
El orquestador crea la rama feat/<feature> al inicio de cada feature, abre una PR al
terminar la feature y espera a que el usuario haga merge antes de continuar.

Estados: pending -> ongoing -> done | blocked
El script gestiona tasks.json; los agentes actualizan progress.md.
"""

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


TASKS_PATH = Path("tasks.json")
PROGRESS_PATH = Path("progress.md")
AGENT_PROMPT_PATH = Path("agent-prompt.md")
AGENTS_DIR = Path(".claude/agents")
LOGS_DIR = Path("logs/agent-loop")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_tasks() -> dict:
    with open(TASKS_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_tasks(data: dict) -> None:
    with open(TASKS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def next_pending(data: dict) -> dict | None:
    return next((t for t in data["tasks"] if t["status"] == "pending"), None)


def set_status(data: dict, task_id: str, status: str, error: str | None = None) -> None:
    for task in data["tasks"]:
        if task["id"] == task_id:
            task["status"] = status
            if status == "ongoing":
                task["started_at"] = now_iso()
            if status == "done":
                task["completed_at"] = now_iso()
                task["error"] = None
            if error is not None:
                task["error"] = error
            return


def build_prompt(task: dict) -> str:
    agent_type = task.get("agent_type", "default-agent")
    agent_file = AGENTS_DIR / f"{agent_type}.md"
    agent_instructions = (
        agent_file.read_text(encoding="utf-8") if agent_file.exists() else ""
    )

    template = AGENT_PROMPT_PATH.read_text(encoding="utf-8")
    progress = (
        PROGRESS_PATH.read_text(encoding="utf-8")
        if PROGRESS_PATH.exists()
        else "(sin progreso aun)"
    )

    prompt = (
        template
        .replace("{{TASK_ID}}", task["id"])
        .replace("{{FEATURE}}", task["feature"])
        .replace("{{FEATURE_TITLE}}", task.get("feature_title", task["feature"]))
        .replace("{{SECTION}}", task["section"])
        .replace("{{TASK_DESCRIPTION}}", task["description"])
        .replace("{{PROGRESS}}", progress)
    )

    if agent_instructions:
        prompt = agent_instructions + "\n\n---\n\n" + prompt
    return prompt


def run_agent(task: dict, prompt: str, log_path: Path) -> tuple[str, int]:
    result = subprocess.run(
        ["claude", "-p", "--dangerously-skip-permissions", prompt],
        capture_output=True,
        text=True,
        timeout=600,
        encoding="utf-8",
    )
    stderr_section = ("\n--- STDERR ---\n" + result.stderr) if result.stderr else ""
    log_path.write_text(result.stdout + stderr_section, encoding="utf-8")
    return result.stdout, result.returncode


def detect_signal(output: str) -> tuple[str, str | None]:
    for line in reversed(output.strip().splitlines()[-30:]):
        line = line.strip()
        if line == "TASK_COMPLETE":
            return "complete", None
        if line.startswith("TASK_BLOCKED:"):
            return "blocked", line[len("TASK_BLOCKED:"):].strip()
        if line.startswith("TASK_FAILED:"):
            return "failed", line[len("TASK_FAILED:"):].strip()
    return "unknown", None


def create_feature_branch(feature: str) -> str:
    branch = f"feat/{feature}"
    subprocess.run(["git", "checkout", "main"], check=True)
    subprocess.run(["git", "pull"], check=True)
    subprocess.run(["git", "checkout", "-b", branch], check=True)
    return branch


def create_pr(feature_title: str, branch: str) -> str:
    result = subprocess.run(
        [
            "gh", "pr", "create",
            "--title", f"feat: {feature_title}",
            "--base", "main",
            "--head", branch,
            "--body", f"Implementación automática de {feature_title}.\n\nGenerado por run-agent-loop.py",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def hitl_feature_pause(feature_title: str, pr_url: str) -> None:
    print(f"\n  Feature completada: {feature_title}")
    print(f"  PR: {pr_url}")
    print("\n  Haz merge de la PR en GitHub y pulsa Enter para continuar con la siguiente feature.")
    input("  > ")
    subprocess.run(["git", "checkout", "main"], check=True)
    subprocess.run(["git", "pull"], check=True)


def summary(data: dict) -> dict:
    counts: dict[str, int] = {"total": len(data["tasks"])}
    for t in data["tasks"]:
        counts[t["status"]] = counts.get(t["status"], 0) + 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic loop orchestrator")
    parser.add_argument("--max-iter", type=int, default=100)
    parser.add_argument("--max-retries", type=int, default=3)
    args = parser.parse_args()

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    data = load_tasks()

    s = summary(data)
    print(f"Agentic loop | max-iter={args.max_iter} max-retries={args.max_retries}")
    print(f"  {s['total']} tareas -- {s.get('pending', 0)} pendientes, {s.get('done', 0)} completadas\n")

    current_feature: str | None = None
    current_branch: str | None = None

    for iteration in range(1, args.max_iter + 1):
        task = next_pending(data)
        if task is None:
            print("Todas las tareas completadas.")
            break

        # Cambio de feature: crear nueva rama
        if task["feature"] != current_feature:
            if current_branch is not None:
                # Cerrar la feature anterior con PR + pausa HITL
                pr_url = create_pr(current_feature_title, current_branch)  # type: ignore[arg-type]
                hitl_feature_pause(current_feature_title, pr_url)  # type: ignore[arg-type]

            current_feature = task["feature"]
            current_feature_title = task.get("feature_title", current_feature)
            print(f"\nIniciando feature: {current_feature_title}")
            current_branch = create_feature_branch(current_feature)
            print(f"  Rama: {current_branch}\n")

        log_path = LOGS_DIR / f"{task['id']}.log"
        desc_preview = task["description"][:70] + ("..." if len(task["description"]) > 70 else "")
        print(f"[{iteration}/{args.max_iter}] {task['id']} -- {desc_preview}")

        set_status(data, task["id"], "ongoing")
        save_tasks(data)

        signal: str
        reason: str | None
        try:
            prompt = build_prompt(task)
            output, _ = run_agent(task, prompt, log_path)
            signal, reason = detect_signal(output)
        except subprocess.TimeoutExpired:
            signal, reason = "failed", "Timeout (600 s)"
        except Exception as exc:
            signal, reason = "failed", str(exc)

        attempts = task.get("attempts", 0) + 1
        task["attempts"] = attempts

        if signal == "complete":
            set_status(data, task["id"], "done")
            print(f"   Completada")
        else:
            if attempts < args.max_retries:
                set_status(data, task["id"], "pending", error=reason)
                print(f"   Reintento {attempts}/{args.max_retries}: {reason}")
            else:
                set_status(data, task["id"], "blocked", error=reason)
                print(f"   Bloqueada tras {attempts} intentos: {reason}")

        save_tasks(data)

    # Cerrar la última feature si quedó pendiente
    if current_branch is not None:
        done_count = sum(1 for t in data["tasks"] if t["status"] == "done")
        if done_count > 0:
            pr_url = create_pr(current_feature_title, current_branch)  # type: ignore[arg-type]
            hitl_feature_pause(current_feature_title, pr_url)  # type: ignore[arg-type]

    s = summary(data)
    print(
        f"\nFin del loop"
        f" -- {s.get('done', 0)} completadas"
        f"  {s.get('pending', 0)} pendientes"
        f"  {s.get('blocked', 0)} bloqueadas"
    )


if __name__ == "__main__":
    main()
