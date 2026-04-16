# GameDevCrew 🎮

**AI-powered development copilot for indie game studios.**

Three specialized LLM agents — an architect, a producer, and a researcher — orchestrated through a single CLI. Every conversation builds your project knowledge base.

```
> @pipeline design weapon upgrade system for a Vampire Survivors-style roguelike

[Pipeline Step 1/2] Claude analyzing architecture...
[Pipeline Step 2/2] GPT extracting decisions...
[Pipeline] Agents done — awaiting review.

╭─── 📋 Pipeline Review — Proposed GDD Entry ───╮
│ Section: Weapon Upgrade System                  │
│ Summary: ScriptableObject-based weapon system   │
│          with 8-level upgrades and evolution...  │
│ Key Decisions:                                  │
│   • Data-driven via ScriptableObjects           │
│   • Separated static/runtime weapon data        │
╰─────────────────────────────────────────────────╯
  [A]pprove   [E]dit   [R]eject   [S]ave raw

Your choice > A
✅ GDD entry 'Weapon Upgrade System' saved. ADR-001 recorded.
```

---

## Why GameDevCrew?

Solo game developers need three kinds of AI help — code, planning, and research. Using a single LLM for all three blurs the output quality. GameDevCrew gives each task to a specialist with its own system prompt, memory, and evaluation criteria.

| Agent | Role | Model | What It Does |
|-------|------|-------|--------------|
| 🤖 Claude | Architect / Coder | claude-opus-4-5 | Unity C# code, architecture, design patterns, debugging |
| ✍️ GPT | Producer / Planner | gpt-4o | Sprint planning, milestone breakdown, MVP scoping |
| 🔍 Gemini | Researcher | gemini-2.5-flash | Unity docs, asset recommendations, competitor analysis |

---

## Key Features

### Multi-Agent Orchestration
Keyword-based router auto-detects task type and sends it to the right agent. Manual override with `@claude`, `@gpt`, `@gemini`, or `@all` for parallel execution.

### Persistent Project Memory
System remembers your project context across sessions — engine, platform, genre, core gameplay. Every agent response is informed by your project, not starting from scratch.

### Pipeline Mode with Agent Chaining
Agents pass outputs to each other. Claude generates architecture → GPT extracts key decisions → auto-generates GDD entries and Architecture Decision Records.

### Human-in-the-Loop Review
Pipeline outputs are never auto-saved. Every proposed GDD/ADR entry goes through a review checkpoint — approve, edit, reject, or save raw. You stay in control.

### GDD & ADR Auto-Generation
Technical discussions automatically become structured project documentation. Your Game Design Document and Architecture Decision Records grow organically through development conversations.

### Graceful Degradation
If any agent's API goes down, the system catches the error and keeps running. The other agents continue working.

---

## Architecture

```
User Input
    ↓
┌─────────────────────────────────────────────────┐
│                  Orchestrator                    │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  │
│  │  Router   │  │ SessionMemory│  │  Pipeline  │  │
│  │ keywords  │  │  per-agent   │  │  Executor  │  │
│  │ + @agent  │  │  history     │  │  chaining  │  │
│  └──────────┘  └──────────────┘  └───────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │           ProjectMemory                   │   │
│  │  project_context.json  (engine, genre...) │   │
│  │  conversation_log.jsonl (full history)    │   │
│  │  decisions.json  (technical decisions)    │   │
│  │  gdd.json  (Game Design Document)        │   │
│  │  adr.json  (Architecture Decision Records)│   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌────────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ ClaudeAgent│ │ GPTAgent │ │ GeminiAgent  │  │
│  │ Anthropic  │ │ OpenAI   │ │ Google AI    │  │
│  └────────────┘ └──────────┘ └──────────────┘  │
└─────────────────────────────────────────────────┘
    ↓                                      ↓
 Terminal Output               data/ (persistent)
```

---

## Quick Start

**1. Clone and install**
```bash
git clone https://github.com/CipherJ98/GameDevCrew.git
cd GameDevCrew
pip install -r requirements.txt
```

**2. Set up API keys**
```bash
cp .env.example .env
# Edit .env with your keys:
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-proj-...
# GEMINI_API_KEY=AI...
```

**3. Run**
```bash
python main.py
```

**4. Set up your project context (optional but recommended)**
```
> @config engine Unity
> @config genre roguelike
> @config platform Steam
```

---

## Usage

### Basic — Auto-routing
```
> How do I implement object pooling in Unity?
[Router] Routed to claude (scores: C=2 GPT=0 Ge=0)
```

### Manual Override
```
> @gpt Break down my roguelike MVP into 2-week sprints
[Router] Manual override → gpt

> @all What's the best approach for a weapon upgrade system?
[Router] Manual override → all agents
```

### Pipeline — Agent Chaining
```
> @pipeline design weapon upgrade system for a Vampire Survivors-style roguelike
[Pipeline Step 1/2] Claude analyzing...
[Pipeline Step 2/2] GPT extracting decisions...
[Pipeline] Review → [A]pprove / [E]dit / [R]eject / [S]ave raw

> @pipeline research enemy AI patterns for top-down roguelikes
[Pipeline Step 1/2] Gemini researching...
[Pipeline Step 2/2] Claude implementing...
```

### Project Memory
```
> @config              # Show current project context
> @config engine Unity # Set a config value
> @history             # Show recent interactions
> @decisions           # Show recorded technical decisions
> @gdd                 # Show Game Design Document
> @adr                 # Show Architecture Decision Records
```

---

## Project Structure

```
GameDevCrew/
├── agents/
│   ├── claude_agent.py      # Architect — Unity code & architecture
│   ├── gpt_agent.py         # Producer — planning & milestones
│   └── gemini_agent.py      # Researcher — docs & competitor analysis
├── core/
│   ├── orchestrator.py      # Task routing + session memory
│   ├── router.py            # Keyword scoring + @agent override
│   ├── pipeline.py          # Agent chaining + review flow
│   └── memory.py            # Persistent project memory layer
├── utils/
│   └── formatter.py         # Rich terminal output formatting
├── api/
│   └── app.py               # FastAPI endpoint (optional)
├── data/                    # Auto-generated, gitignored
│   ├── project_context.json # Project metadata
│   ├── conversation_log.jsonl
│   ├── decisions.json
│   ├── gdd.json
│   ├── adr.json
│   └── raw_outputs/         # Saved pipeline raw outputs
├── main.py                  # CLI entry point
├── .env.example             # API key template
└── requirements.txt
```

---

## Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Routing | Keyword scoring over LLM classifier | Predictability > intelligence for dev tools |
| Agent memory | Separated per-agent over shared context | Prevents role contamination between specialists |
| Interface | CLI-first over web UI | Fits developer workflow; ship fast |
| Pipeline saves | Human approval required | Human-in-the-loop > auto-save for project docs |
| Data format | JSON/JSONL files over database | Zero dependencies; easy to inspect and version |

---

## Roadmap

- [ ] Research-first pipeline (Gemini → Claude)
- [ ] Sprint report generation from conversation history
- [ ] Embedding-based semantic routing
- [ ] Code review pipeline (paste code → multi-agent review)
- [ ] Web dashboard for GDD/ADR visualization
- [ ] Multi-project support

---

## Tech Stack

Python, FastAPI, Rich (terminal UI), Claude API (Anthropic), GPT-4o (OpenAI), Gemini 2.5 Flash (Google AI)

---

## Video Series

This project is documented in a 3-part YouTube series covering the full product lifecycle:

- **[Episode 1: Why I Built This](https://youtube.com/@CipherJCodeCraft)** — Problem discovery, product decisions, live demo
- **Episode 2: How It Works** — Orchestration, pipeline, memory layer *(coming soon)*
- **Episode 3: What I Learned** — Iteration, failures, roadmap *(coming soon)*

---

## Built By

**Christopher Chen (CipherJ)** — ex-EA Shanghai (FIFA Mobile), indie game developer, AI tools builder.

- YouTube: [@CipherJCodeCraft](https://youtube.com/@CipherJCodeCraft)
- GitHub: [@CipherJ98](https://github.com/CipherJ98)
- LinkedIn: [Christopher Chen](https://linkedin.com/in/christopherchen98)
