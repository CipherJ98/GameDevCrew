import json
import time
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from core.memory import ProjectMemory, DATA_DIR
from utils.formatter import console

GDD_PATH = os.path.join(DATA_DIR, "gdd.json")
ADR_PATH = os.path.join(DATA_DIR, "adr.json")
RAW_OUTPUTS_DIR = os.path.join(DATA_DIR, "raw_outputs")
PENDING_REVIEW_PATH = os.path.join(DATA_DIR, ".pending_review.json")

GPT_EXTRACTION_PROMPT = """You are a technical producer. You have just received a technical architecture document from the lead architect.
Your job is to:
1. Extract the key technical decisions made
2. Summarize the approach in 2-3 sentences
3. Identify what alternatives were implicitly rejected
4. Output a JSON object with fields: section_name, summary, technical_approach, key_decisions, alternatives_considered, consequences
Respond ONLY with valid JSON. No markdown, no explanation."""


@dataclass
class PipelineResult:
    """Holds the output of a design-doc pipeline run, pending review."""
    task: str
    claude_output: str
    gpt_raw_output: str
    gpt_extracted_json: dict = field(default_factory=dict)
    proposed_gdd_entry: dict = field(default_factory=dict)
    proposed_adr_entry: dict = field(default_factory=dict)
    status: str = "pending"           # pending / approved / rejected
    json_valid: bool = True


class PipelineExecutor:
    """Chains agent outputs through multi-step pipelines."""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.project_memory = orchestrator.project_memory

    # ── Design Doc Pipeline ──────────────────────────────────

    def run_design_doc(self, task: str) -> PipelineResult | None:
        """Claude → GPT extraction → return PipelineResult for review."""
        console.print(f"\n[bold magenta][Pipeline] Starting design-doc pipeline[/bold magenta]")
        console.print(f"[dim]Task: {task}[/dim]\n")

        # Step 1: Claude produces technical architecture
        console.print("[bold cyan][Pipeline Step 1/2] Claude analyzing architecture...[/bold cyan]")
        try:
            claude_output = self.orchestrator.claude.run(task)
        except Exception as e:
            console.print(f"[red]Claude failed: {e}[/red]")
            return None
        self.project_memory.log_interaction("claude", task, claude_output)
        console.print(claude_output)
        console.print()
        time.sleep(2)

        # Step 2: GPT extracts structured GDD/ADR
        console.print("[bold green][Pipeline Step 2/2] GPT extracting decisions...[/bold green]")
        extraction_task = (
            f"{GPT_EXTRACTION_PROMPT}\n\n"
            f"--- ARCHITECT OUTPUT ---\n{claude_output}\n"
            f"--- ORIGINAL TASK ---\n{task}"
        )
        try:
            gpt_output = self.orchestrator.gpt.run(extraction_task)
        except Exception as e:
            console.print(f"[red]GPT failed: {e}[/red]")
            return None
        self.project_memory.log_interaction("gpt", "extract decisions from architecture", gpt_output)
        console.print(gpt_output)
        console.print()
        time.sleep(2)

        # Build PipelineResult
        data, json_valid = self._parse_gpt_json(gpt_output)
        result = PipelineResult(
            task=task,
            claude_output=claude_output,
            gpt_raw_output=gpt_output,
            gpt_extracted_json=data,
            json_valid=json_valid,
        )

        if json_valid:
            result.proposed_gdd_entry, result.proposed_adr_entry = self._build_entries(task, data)

        console.print("[bold magenta][Pipeline] Agents done — awaiting review.[/bold magenta]\n")
        return result

    # ── Research-First Pipeline ──────────────────────────────

    def run_research_first(self, task: str) -> str | None:
        """Gemini researches → Claude codes. Returns Claude output for optional save."""
        console.print(f"\n[bold magenta][Pipeline] Starting research-first pipeline[/bold magenta]")
        console.print(f"[dim]Task: {task}[/dim]\n")

        # Step 1: Gemini researches
        console.print("[bold yellow][Pipeline Step 1/2] Gemini researching...[/bold yellow]")
        try:
            gemini_output = self.orchestrator.gemini.run(task)
        except Exception as e:
            console.print(f"[red]Gemini failed: {e}[/red]")
            return None
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
            return None
        self.project_memory.log_interaction("claude", task, claude_output)
        console.print(claude_output)
        console.print("[bold magenta][Pipeline] Research-first pipeline complete![/bold magenta]\n")
        return claude_output
    
    # ── Art Brifet Pipeline ────────────────────────────────
    def run_art_brief(self,description:str):
        """Game designer describes the plan -> structure the art brief -> pass to human review"""
        from agents.artbrief_agent import ArtBriefAgent

        console.print("\n[bold cyan][ArtBrief Pipeline][/bold cyan] Processing description...")

        agent = ArtBriefAgent()
        result = agent.run(description)

        if not result["success"]:
            console.print(f"[red]Failed to parse output: {result['error']}[/red]")
            console.print(f"[dim]Raw output:\n{result['raw']}[/dim]")
            return None

        return result["data"]
    
    # ── Art Asset Validation ────────────────────────────────
    def run_asset_validation(self,folder_path:str):
        from agents.asset_validator_agent import AssetValidatorAgent
        console.print(f"\n[dim]folder_path received: '{folder_path}'[/dim]") 
        console.print("\n[bold cyan][AssetValidation Pipeline][/bold cyan] Scanning folder...")
        agent = AssetValidatorAgent()
        agent.run(folder_path)
        return agent.run(folder_path)
    
    # ── Art Vision Validation ────────────────────────────────
    def run_vision_check(self, image_path: str, brief_path: str):
        from agents.vision_validator_agent import VisionValidatorAgent
        import json
        
        console.print("\n[bold cyan][Vision Check Pipeline][/bold cyan] Analyzing image...")
        
        if not os.path.exists(brief_path):
            console.print(f"[red]Brief文件不存在: {brief_path}[/red]")
            return None
        
        with open(brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)
        
        agent = VisionValidatorAgent()
        return agent.run(image_path, brief)

    # ── Review / Save methods ────────────────────────────────

    def save_approved_result(self, result: PipelineResult) -> str:
        """Save an approved PipelineResult to GDD and ADR. Returns ADR id."""
        result.status = "approved"
        adr_id = self._write_gdd_adr(result.task, result.gpt_extracted_json)
        return adr_id

    def save_with_edits(self, result: PipelineResult, edited_json: dict) -> str:
        """Save with user-edited JSON. Returns ADR id."""
        result.status = "approved"
        result.gpt_extracted_json = edited_json
        result.proposed_gdd_entry, result.proposed_adr_entry = self._build_entries(result.task, edited_json)
        adr_id = self._write_gdd_adr(result.task, edited_json)
        return adr_id

    def save_raw_output(self, task: str, content: str) -> str:
        """Save raw agent output to data/raw_outputs/. Returns file path."""
        os.makedirs(RAW_OUTPUTS_DIR, exist_ok=True)
        slug = re.sub(r'[^a-z0-9]+', '_', task.lower()).strip('_')[:60]
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}_{slug}.md"
        path = os.path.join(RAW_OUTPUTS_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {task}\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n---\n\n")
            f.write(content)
        return path

    # ── Internal helpers ─────────────────────────────────────

    @staticmethod
    def _parse_gpt_json(gpt_output: str) -> tuple[dict, bool]:
        """Try to parse GPT output as JSON. Returns (data, is_valid)."""
        try:
            text = gpt_output.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
            data = json.loads(text)
            return data, True
        except json.JSONDecodeError:
            return {}, False

    def _build_entries(self, task: str, data: dict) -> tuple[dict, dict]:
        """Build proposed GDD and ADR entries from extracted data."""
        section_name = data.get("section_name", "unnamed_section")
        now = datetime.now().isoformat()
        project_name = self.project_memory.get_context().get("project_name", "GameDevCrew Project")

        gdd_entry = {
            "section_name": section_name,
            "summary": data.get("summary", ""),
            "technical_approach": data.get("technical_approach", ""),
            "key_decisions": data.get("key_decisions", []),
            "created": now,
            "source_task": task,
        }

        # Figure out next ADR id
        adr = self._load_json(ADR_PATH, {"records": []})
        next_id = f"ADR-{len(adr['records']) + 1:03d}"

        adr_entry = {
            "id": next_id,
            "title": section_name.replace("_", " ").title(),
            "date": now,
            "status": "accepted",
            "context": task,
            "decision": data.get("summary", ""),
            "alternatives_considered": data.get("alternatives_considered", []),
            "consequences": data.get("consequences", ""),
            "source_agent": "claude → gpt",
        }

        return gdd_entry, adr_entry

    def _write_gdd_adr(self, task: str, data: dict) -> str:
        """Persist GDD section + ADR record. Returns ADR id."""
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
        return adr_id

    def write_pending_review(self, data: dict):
        """Write proposed JSON to temp file for user editing."""
        os.makedirs(DATA_DIR, exist_ok=True)
        self._write_json(PENDING_REVIEW_PATH, data)

    def read_pending_review(self) -> tuple[dict | None, str | None]:
        """Read back the edited pending review file. Returns (data, error)."""
        if not os.path.exists(PENDING_REVIEW_PATH):
            return None, "File not found"
        try:
            with open(PENDING_REVIEW_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data, None
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON: {e}"

    def cleanup_pending_review(self):
        """Remove temp review file."""
        if os.path.exists(PENDING_REVIEW_PATH):
            os.remove(PENDING_REVIEW_PATH)

    @staticmethod
    def _load_json(path, default):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    @staticmethod
    def _write_json(path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
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
