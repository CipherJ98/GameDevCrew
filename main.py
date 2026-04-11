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
from core import Orchestrator
from core.pipeline import PipelineExecutor
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

[magenta]Pipelines:[/magenta]
  @pipeline design "topic" — Claude architects → GPT extracts → saves GDD/ADR
  @pipeline research "topic" — Gemini researches → Claude implements
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

def handle_config(orchestrator: Orchestrator, args: str):
    """Handle @config command."""
    args = args.strip()
    if not args:
        # Show current config
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
        # Truncate long tasks
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
        pipeline.run_design_doc(topic)
    elif pipeline_type == "research":
        pipeline.run_research_first(topic)
    else:
        console.print(f"[red]Unknown pipeline type '{pipeline_type}'. Use 'design' or 'research'.[/red]")

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
