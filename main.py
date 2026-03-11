"""
GameDevCrew — Your AI Game Development Team
============================================
Claude   → Code, C# scripts, Unity architecture
GPT      → Copywriting, Steam descriptions, marketing
Gemini   → Research, Unity docs, asset recommendations

Usage:
    python main.py                  # Interactive mode
    python main.py "your task"      # Single task mode
"""

import sys
import os
from dotenv import load_dotenv
from core import Orchestrator
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
║      🎮 GameDevCrew v0.1             ║
║   Your AI Game Development Team      ║
╚══════════════════════════════════════╝[/bold cyan]

[cyan]Claude[/cyan]  → Code & Unity architecture
[green]GPT[/green]     → Copywriting & marketing  
[yellow]Gemini[/yellow]  → Research & documentation

[dim]Type 'quit' to exit | 'help' for example tasks[/dim]
""")

EXAMPLE_TASKS = """
[bold]Example tasks you can try:[/bold]

[cyan]Code (→ Claude):[/cyan]
  • Write a Unity C# singleton pattern for a GameManager
  • Debug this error: NullReferenceException in PlayerController
  • How do I implement object pooling in Unity?

[green]Writing (→ GPT):[/green]
  • Write a Steam description for my 2D platformer about a time-traveling cat
  • Create a devlog post announcing my new enemy AI system

[yellow]Research (→ Gemini):[/yellow]
  • What are the best Unity assets for procedural generation?
  • Find documentation on Unity's new Input System
  • What indie games are similar to mine: pixel art roguelike?
"""

def run_interactive(orchestrator: Orchestrator):
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
