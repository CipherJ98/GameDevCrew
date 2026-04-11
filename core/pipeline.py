import json
import time
import os
from datetime import datetime
from core.memory import ProjectMemory, DATA_DIR
from utils.formatter import console

GDD_PATH = os.path.join(DATA_DIR, "gdd.json")
ADR_PATH = os.path.join(DATA_DIR, "adr.json")

GPT_EXTRACTION_PROMPT = """You are a technical producer. You have just received a technical architecture document from the lead architect.
Your job is to:
1. Extract the key technical decisions made
2. Summarize the approach in 2-3 sentences
3. Identify what alternatives were implicitly rejected
4. Output a JSON object with fields: section_name, summary, technical_approach, key_decisions, alternatives_considered, consequences
Respond ONLY with valid JSON. No markdown, no explanation."""


class PipelineExecutor:
    """Chains agent outputs through multi-step pipelines."""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.project_memory = orchestrator.project_memory

    # ── Design Doc Pipeline ──────────────────────────────────

    def run_design_doc(self, task: str):
        """Claude → GPT → auto-save GDD + ADR."""
        console.print(f"\n[bold magenta][Pipeline] Starting design-doc pipeline[/bold magenta]")
        console.print(f"[dim]Task: {task}[/dim]\n")

        # Step 1: Claude produces technical architecture
        console.print("[bold cyan][Pipeline Step 1/3] Claude analyzing architecture...[/bold cyan]")
        try:
            claude_output = self.orchestrator.claude.run(task)
        except Exception as e:
            console.print(f"[red]Claude failed: {e}[/red]")
            return
        self.project_memory.log_interaction("claude", task, claude_output)
        console.print(claude_output)
        console.print()
        time.sleep(2)

        # Step 2: GPT extracts structured GDD/ADR
        console.print("[bold green][Pipeline Step 2/3] GPT extracting decisions...[/bold green]")
        extraction_task = (
            f"{GPT_EXTRACTION_PROMPT}\n\n"
            f"--- ARCHITECT OUTPUT ---\n{claude_output}\n"
            f"--- ORIGINAL TASK ---\n{task}"
        )
        try:
            gpt_output = self.orchestrator.gpt.run(extraction_task)
        except Exception as e:
            console.print(f"[red]GPT failed: {e}[/red]")
            return
        self.project_memory.log_interaction("gpt", "extract decisions from architecture", gpt_output)
        console.print(gpt_output)
        console.print()
        time.sleep(2)

        # Step 3: Parse and save
        console.print("[bold yellow][Pipeline Step 3/3] Saving GDD & ADR...[/bold yellow]")
        self._save_gdd_adr(task, gpt_output)
        console.print("[bold magenta][Pipeline] Design-doc pipeline complete![/bold magenta]\n")

    # ── Research-First Pipeline ──────────────────────────────

    def run_research_first(self, task: str):
        """Gemini researches → Claude codes informed by research."""
        console.print(f"\n[bold magenta][Pipeline] Starting research-first pipeline[/bold magenta]")
        console.print(f"[dim]Task: {task}[/dim]\n")

        # Step 1: Gemini researches
        console.print("[bold yellow][Pipeline Step 1/2] Gemini researching...[/bold yellow]")
        try:
            gemini_output = self.orchestrator.gemini.run(task)
        except Exception as e:
            console.print(f"[red]Gemini failed: {e}[/red]")
            return
        self.project_memory.log_interaction("gemini", task, gemini_output)
        console.print(gemini_output)
        console.print()
        time.sleep(2)

        # Step 2: Claude codes with research context
        console.print("[bold cyan][Pipeline Step 2/2] Claude implementing with research...[/bold cyan]")
        claude_task = (
            f"Based on the following research, implement a solution for: {task}\n\n"
            f"--- RESEARCH FINDINGS ---\n{gemini_output}"
        )
        try:
            claude_output = self.orchestrator.claude.run(claude_task)
        except Exception as e:
            console.print(f"[red]Claude failed: {e}[/red]")
            return
        self.project_memory.log_interaction("claude", task, claude_output)
        console.print(claude_output)
        console.print("[bold magenta][Pipeline] Research-first pipeline complete![/bold magenta]\n")

    # ── GDD / ADR persistence ────────────────────────────────

    def _save_gdd_adr(self, task: str, gpt_output: str):
        """Parse GPT JSON output and append to GDD + ADR files."""
        try:
            # Strip markdown code fences if present
            text = gpt_output.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]  # remove first line
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
            data = json.loads(text)
        except json.JSONDecodeError:
            console.print("[yellow]Warning: GPT did not return valid JSON. Saving raw text.[/yellow]")
            data = {
                "section_name": "unparsed",
                "summary": gpt_output[:200],
                "technical_approach": "",
                "key_decisions": [],
                "alternatives_considered": [],
                "consequences": "",
            }

        section_name = data.get("section_name", "unnamed_section")
        now = datetime.now().isoformat()
        project_name = self.project_memory.get_context().get("project_name", "GameDevCrew Project")

        # ── Save GDD ──
        gdd = self._load_json(GDD_PATH, {
            "project_name": project_name,
            "last_updated": now,
            "sections": {}
        })
        gdd["last_updated"] = now
        gdd["project_name"] = project_name
        gdd["sections"][section_name] = {
            "summary": data.get("summary", ""),
            "technical_approach": data.get("technical_approach", ""),
            "key_decisions": data.get("key_decisions", []),
            "created": now,
            "source_task": task,
        }
        self._write_json(GDD_PATH, gdd)
        console.print(f"  [green]GDD section '{section_name}' saved.[/green]")

        # ── Save ADR ──
        adr = self._load_json(ADR_PATH, {"records": []})
        adr_id = f"ADR-{len(adr['records']) + 1:03d}"
        adr["records"].append({
            "id": adr_id,
            "title": section_name.replace("_", " ").title(),
            "date": now,
            "status": "accepted",
            "context": task,
            "decision": data.get("summary", ""),
            "alternatives_considered": data.get("alternatives_considered", []),
            "consequences": data.get("consequences", ""),
            "source_agent": "claude → gpt",
        })
        self._write_json(ADR_PATH, adr)
        console.print(f"  [green]{adr_id} saved.[/green]")

    @staticmethod
    def _load_json(path, default):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    @staticmethod
    def _write_json(path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ── Display helpers ──────────────────────────────────────

    @staticmethod
    def show_gdd():
        if not os.path.exists(GDD_PATH):
            console.print("[dim]No GDD data yet. Run @pipeline design first.[/dim]")
            return
        with open(GDD_PATH, "r", encoding="utf-8") as f:
            gdd = json.load(f)
        console.print(f"\n[bold]Game Design Document — {gdd.get('project_name', 'Unnamed')}[/bold]")
        console.print(f"[dim]Last updated: {gdd.get('last_updated', 'N/A')}[/dim]\n")
        for name, section in gdd.get("sections", {}).items():
            console.print(f"  [bold cyan]{name}[/bold cyan]")
            console.print(f"    Summary: {section.get('summary', '')}")
            console.print(f"    Approach: {section.get('technical_approach', '')}")
            decisions = section.get("key_decisions", [])
            if decisions:
                console.print(f"    Decisions: {', '.join(decisions) if isinstance(decisions, list) else decisions}")
            console.print()

    @staticmethod
    def show_adr():
        if not os.path.exists(ADR_PATH):
            console.print("[dim]No ADR records yet. Run @pipeline design first.[/dim]")
            return
        with open(ADR_PATH, "r", encoding="utf-8") as f:
            adr = json.load(f)
        console.print(f"\n[bold]Architecture Decision Records[/bold]\n")
        for rec in adr.get("records", []):
            console.print(f"  [bold yellow]{rec['id']}[/bold yellow] — {rec.get('title', '')}")
            console.print(f"    Status: {rec.get('status', '')}")
            console.print(f"    Decision: {rec.get('decision', '')}")
            alts = rec.get("alternatives_considered", [])
            if alts:
                console.print(f"    Alternatives: {', '.join(alts) if isinstance(alts, list) else alts}")
            console.print(f"    Consequences: {rec.get('consequences', '')}")
            console.print()
