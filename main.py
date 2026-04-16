"""
GameDevCrew — Your AI Game Development Team
============================================
Claude   → Code, C# scripts, Unity architecture
GPT      → Production planning, milestones, roadmaps
Gemini   → Research, Unity docs, asset recommendations

Usage:
    python main.py                  # Interactive mode
    python main.py "your task"      # Single task mode
"""

import sys
import os
import json
from dotenv import load_dotenv
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from core import Orchestrator
from core.pipeline import PipelineExecutor, PipelineResult
from utils import format_response, console

load_dotenv()

def check_env():
    """Make sure all API keys are loaded."""
    missing = []
    for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]:
        if not os.getenv(key):
            missing.append(key)
    if missing:
        console.print(f"[red]Missing API keys: {', '.join(missing)}[/red]")
        console.print("[dim]Copy .env.example to .env and fill in your keys[/dim]")
        sys.exit(1)

def print_banner():
    console.print("""
[bold cyan]╔══════════════════════════════════════╗
║      🎮 GameDevCrew v0.2             ║
║   Your AI Game Development Team      ║
╚══════════════════════════════════════╝[/bold cyan]

[cyan]Claude[/cyan]  → Code & Unity architecture
[green]GPT[/green]     → Production planning & milestones
[yellow]Gemini[/yellow]  → Research & documentation

[dim]Type 'quit' to exit | 'help' for commands[/dim]
""")

EXAMPLE_TASKS = """
[bold]Commands:[/bold]

[magenta]Memory & Config:[/magenta]
  @config                — show current project config
  @config key value      — set a config value (e.g. @config engine Unity)
  @history               — show last 10 interactions
  @decisions             — show all recorded decisions

[magenta]Pipeline (agent chaining):[/magenta]
  • @pipeline design "weapon upgrade system" — Claude→GPT→Review→GDD/ADR
  • @pipeline research "enemy AI patterns"   — Gemini→Claude→Save
  All pipeline outputs go through review before saving.
  @gdd                   — display current Game Design Document
  @adr                   — display Architecture Decision Records

[bold]Example tasks:[/bold]

[cyan]Code (→ Claude):[/cyan]
  • Write a Unity C# singleton pattern for a GameManager
  • Debug this error: NullReferenceException in PlayerController
  • How do I implement object pooling in Unity?

[green]Planning (→ GPT):[/green]
  • Break down a free-flow combat system into weekly milestones
  • Create a 2-week sprint plan for my Unity army battle prototype
  • What should I build first for my roguelike MVP?

[yellow]Research (→ Gemini):[/yellow]
  • What are the best Unity assets for procedural generation?
  • Find documentation on Unity's new Input System
  • What indie games are similar to mine: pixel art roguelike?
"""

# ── Memory & Config Handlers ────────────────────────────────

def handle_config(orchestrator: Orchestrator, args: str):
    """Handle @config command."""
    args = args.strip()
    if not args:
        ctx = orchestrator.project_memory.get_context()
        console.print("\n[bold]Project Configuration:[/bold]")
        for key, value in ctx.items():
            display = value if value else "[dim]not set[/dim]"
            console.print(f"  [cyan]{key}[/cyan]: {display}")
        console.print()
        return

    parts = args.split(None, 1)
    if len(parts) < 2:
        console.print("[red]Usage: @config key value (e.g. @config engine Unity)[/red]")
        return

    key, value = parts
    orchestrator.project_memory.set_context(key, value)
    orchestrator.refresh_context()
    console.print(f"[green]Set {key} = {value}[/green]")

def handle_history(orchestrator: Orchestrator):
    """Handle @history command."""
    entries = orchestrator.project_memory.get_history(10)
    if not entries:
        console.print("[dim]No interaction history yet.[/dim]")
        return
    console.print(f"\n[bold]Last {len(entries)} interactions:[/bold]\n")
    for entry in entries:
        ts = entry.get("timestamp", "")[:19]
        agent = entry.get("agent", "?").upper()
        task = entry.get("task", "")
        if len(task) > 80:
            task = task[:77] + "..."
        console.print(f"  [dim]{ts}[/dim] [{agent}] {task}")
    console.print()

def handle_decisions(orchestrator: Orchestrator):
    """Handle @decisions command."""
    decisions = orchestrator.project_memory.get_decisions()
    if not decisions:
        console.print("[dim]No decisions recorded yet.[/dim]")
        return
    console.print(f"\n[bold]Recorded Decisions ({len(decisions)}):[/bold]\n")
    for d in decisions:
        ts = d.get("timestamp", "")[:19]
        console.print(f"  [bold yellow]{d.get('topic', '')}[/bold yellow]")
        console.print(f"    Decision: {d.get('decision', '')}")
        console.print(f"    Reasoning: {d.get('reasoning', '')}")
        console.print(f"    Agent: {d.get('agent_source', '')} | {ts}")
        console.print()

# ── Pipeline Review UI ──────────────────────────────────────

def _display_proposed_entry(result: PipelineResult):
    """Show the proposed GDD/ADR entry in a Rich panel for review."""
    data = result.gpt_extracted_json

    section = data.get("section_name", "unnamed")
    summary = data.get("summary", "")
    approach = data.get("technical_approach", "")
    decisions = data.get("key_decisions", [])
    alternatives = data.get("alternatives_considered", [])
    consequences = data.get("consequences", "")

    lines = []
    lines.append(f"[bold green]Section:[/bold green] {section}")
    lines.append(f"[white]Summary:[/white] {summary}")
    lines.append(f"[white]Approach:[/white] {approach}")

    if decisions:
        lines.append("[white]Key Decisions:[/white]")
        for d in (decisions if isinstance(decisions, list) else [decisions]):
            lines.append(f"  • {d}")

    if alternatives:
        lines.append("[dim]Alternatives Considered:[/dim]")
        for a in (alternatives if isinstance(alternatives, list) else [alternatives]):
            lines.append(f"  [dim]• {a}[/dim]")

    if consequences:
        lines.append(f"[dim]Consequences:[/dim] {consequences}")

    body = "\n".join(lines)

    console.print(Panel(
        body,
        title="[bold white]📋 Pipeline Review — Proposed GDD Entry[/bold white]",
        border_style="magenta",
        box=box.DOUBLE,
        padding=(1, 2),
    ))

    console.print(Panel(
        "  [bold green]\\[A][/bold green]pprove   "
        "[bold yellow]\\[E][/bold yellow]dit   "
        "[bold red]\\[R][/bold red]eject   "
        "[bold blue]\\[S][/bold blue]ave raw",
        border_style="magenta",
        box=box.DOUBLE,
        padding=(0, 2),
    ))


def _review_design_result(pipeline: PipelineExecutor, result: PipelineResult):
    """Interactive review loop for a design-doc pipeline result."""

    # If GPT JSON was invalid, skip structured review
    if not result.json_valid:
        console.print("[yellow]GPT did not return valid JSON — structured review unavailable.[/yellow]")
        console.print("[dim]You can save Claude's raw architecture output instead.[/dim]\n")
        choice = _ask_choice("Save Claude's raw output? [Y/N]", ["y", "n"])
        if choice == "y":
            path = pipeline.save_raw_output(result.task, result.claude_output)
            console.print(f"💾 Raw output saved to [cyan]{path}[/cyan]")
        else:
            console.print("❌ Nothing saved.")
        return

    _display_proposed_entry(result)

    while True:
        choice = _ask_choice("Your choice", ["a", "e", "r", "s"])

        if choice == "a":
            adr_id = pipeline.save_approved_result(result)
            section = result.gpt_extracted_json.get("section_name", "")
            console.print(f"✅ GDD entry [green]'{section}'[/green] saved. [green]{adr_id}[/green] recorded.")
            pipeline.cleanup_pending_review()
            break

        elif choice == "e":
            _handle_edit_flow(pipeline, result)
            break

        elif choice == "r":
            result.status = "rejected"
            pipeline.project_memory.log_interaction(
                "pipeline", result.task,
                f"[REJECTED] Design-doc pipeline output rejected by user."
            )
            console.print("❌ Rejected. Nothing saved.")
            pipeline.cleanup_pending_review()
            break

        elif choice == "s":
            path = pipeline.save_raw_output(result.task, result.claude_output)
            console.print(f"💾 Raw output saved to [cyan]{path}[/cyan]")
            pipeline.cleanup_pending_review()
            break


def _handle_edit_flow(pipeline: PipelineExecutor, result: PipelineResult):
    """Write JSON to temp file, wait for user edit, validate, save."""
    pipeline.write_pending_review(result.gpt_extracted_json)
    review_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", ".pending_review.json")
    console.print(f"\n[bold]Edit the file at:[/bold] [cyan]{review_path}[/cyan]")
    console.print("[dim]Press Enter when done editing.[/dim]")

    while True:
        console.input("[bold white]>[/bold white] ")
        edited_data, error = pipeline.read_pending_review()
        if error:
            console.print(f"[red]{error}[/red]")
            console.print("[dim]Fix the JSON and press Enter to try again, or type 'cancel' to abort.[/dim]")
            cancel_check = console.input("[bold white]>[/bold white] ").strip().lower()
            if cancel_check == "cancel":
                console.print("❌ Edit cancelled. Nothing saved.")
                pipeline.cleanup_pending_review()
                return
            # Re-read after they had another chance
            edited_data, error = pipeline.read_pending_review()
            if error:
                console.print(f"[red]Still invalid: {error}[/red]")
                console.print("❌ Edit cancelled. Nothing saved.")
                pipeline.cleanup_pending_review()
                return

        adr_id = pipeline.save_with_edits(result, edited_data)
        section = edited_data.get("section_name", "")
        console.print(f"✅ GDD entry [green]'{section}'[/green] saved (edited). [green]{adr_id}[/green] recorded.")
        pipeline.cleanup_pending_review()
        return


def _review_research_result(pipeline: PipelineExecutor, task: str, claude_output: str):
    """Simple Y/N confirmation to save research pipeline output."""
    console.print("[Pipeline] Research complete. Save Claude's implementation to raw outputs?")
    choice = _ask_choice("  [Y]es  [N]o", ["y", "n"])
    if choice == "y":
        path = pipeline.save_raw_output(task, claude_output)
        console.print(f"💾 Saved to [cyan]{path}[/cyan]")
    else:
        console.print("[dim]Output not saved.[/dim]")


def _ask_choice(prompt_text: str, valid: list[str]) -> str:
    """Keep asking until user gives a valid single-char choice."""
    while True:
        raw = console.input(f"[bold white]{prompt_text}[/bold white] > ").strip().lower()
        if raw and raw[0] in valid:
            return raw[0]
        valid_display = "/".join(v.upper() for v in valid)
        console.print(f"[red]Please enter one of: {valid_display}[/red]")


# ── Pipeline Command Handler ────────────────────────────────

def handle_pipeline(orchestrator: Orchestrator, pipeline: PipelineExecutor, args: str):
    """Handle @pipeline command."""
    args = args.strip()
    if not args:
        console.print("[red]Usage: @pipeline design \"topic\" or @pipeline research \"topic\"[/red]")
        return

    parts = args.split(None, 1)
    pipeline_type = parts[0].lower()
    topic = parts[1].strip('"\'') if len(parts) > 1 else ""

    if not topic:
        console.print("[red]Please provide a topic after the pipeline type.[/red]")
        return

    if pipeline_type == "design":
        result = pipeline.run_design_doc(topic)
        if result is not None:
            _review_design_result(pipeline, result)
    elif pipeline_type == "research":
        claude_output = pipeline.run_research_first(topic)
        if claude_output is not None:
            _review_research_result(pipeline, topic, claude_output)
    else:
        console.print(f"[red]Unknown pipeline type '{pipeline_type}'. Use 'design' or 'research'.[/red]")


# ── Interactive REPL ─────────────────────────────────────────

def run_interactive(orchestrator: Orchestrator):
    pipeline = PipelineExecutor(orchestrator)

    while True:
        try:
            task = console.input("\n[bold white]>[/bold white] ").strip()

            if not task:
                continue
            if task.lower() in ("quit", "exit", "q"):
                console.print("[dim]Goodbye! Go ship that game 🚀[/dim]")
                break
            if task.lower() == "help":
                console.print(EXAMPLE_TASKS)
                continue

            # Memory & config commands
            if task.lower().startswith("@config"):
                handle_config(orchestrator, task[7:])
                continue
            if task.lower() == "@history":
                handle_history(orchestrator)
                continue
            if task.lower() == "@decisions":
                handle_decisions(orchestrator)
                continue

            # Pipeline commands
            if task.lower().startswith("@pipeline"):
                handle_pipeline(orchestrator, pipeline, task[9:])
                continue
            if task.lower() == "@gdd":
                PipelineExecutor.show_gdd()
                continue
            if task.lower() == "@adr":
                PipelineExecutor.show_adr()
                continue

            result = orchestrator.run(task, verbose=True)
            format_response(result)

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Goodbye![/dim]")
            break

def main():
    check_env()
    orchestrator = Orchestrator()

    # Single task mode: python main.py "your task here"
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        result = orchestrator.run(task, verbose=True)
        format_response(result)
        return

    # Interactive mode
    print_banner()
    run_interactive(orchestrator)

if __name__ == "__main__":
    main()
