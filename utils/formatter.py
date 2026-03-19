from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import time

console = Console()

AGENT_COLORS = {
    "claude": "cyan",
    "gpt": "green",
    "gemini": "yellow",
}

AGENT_LABELS = {
    "claude": "🤖 CLAUDE — Code & Architecture",
    "gpt": "✍️  GPT — Production & Planning",
    "gemini": "🔍 GEMINI — Research & Docs",
}

def stream_text(text: str, delay: float = 0.01):
    """Print text line by line with a small delay for recording."""
    lines = text.split('\n')
    for line in lines:
        console.print(line)
        time.sleep(delay)

def format_response(result: dict):
    """Pretty print the orchestrator output using Rich."""
    
    console.print(f"\n[bold white]Task:[/bold white] {result['task']}")
    console.print(f"[dim]Routing: {result['routing_reason']}[/dim]\n")

    for agent_name, response in result["results"].items():
        color = AGENT_COLORS.get(agent_name, "white")
        label = AGENT_LABELS.get(agent_name, agent_name.upper())
        
        # Print header panel without content
        console.print(Panel(
            "",
            title=f"[bold {color}]{label}[/bold {color}]",
            border_style=color,
            box=box.ROUNDED,
            padding=(0, 2)
        ))
        
        # Stream content line by line
        stream_text(response, delay=0.07)
        console.print()