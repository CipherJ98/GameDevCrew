from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

AGENT_COLORS = {
    "claude": "cyan",
    "gpt": "green",
    "gemini": "yellow",
}

AGENT_LABELS = {
    "claude": "🤖 CLAUDE — Code & Architecture",
    "gpt": "✍️  GPT — Copywriting & Marketing",
    "gemini": "🔍 GEMINI — Research & Docs",
}

def format_response(result: dict):
    """Pretty print the orchestrator output using Rich."""
    
    console.print(f"\n[bold white]Task:[/bold white] {result['task']}")
    console.print(f"[dim]Routing: {result['routing_reason']}[/dim]\n")

    for agent_name, response in result["results"].items():
        color = AGENT_COLORS.get(agent_name, "white")
        label = AGENT_LABELS.get(agent_name, agent_name.upper())
        
        console.print(Panel(
            response,
            title=f"[bold {color}]{label}[/bold {color}]",
            border_style=color,
            box=box.ROUNDED,
            padding=(1, 2)
        ))
