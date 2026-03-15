# GameDevCrew 🎮

A multi-agent AI orchestration system for indie game developers.
Routes tasks across Claude, GPT-4o, and Gemini based on task type —
so every job goes to the model best suited for it.

---

## What It Does

| Agent | Model | Specialization |
|-------|-------|----------------|
| Claude | claude-opus-4-5 | Unity C# code, architecture, debugging |
| GPT | gpt-4o | Steam descriptions, devlogs, marketing copy |
| Gemini | gemini-2.0-flash | Unity docs research, asset recommendations |

---

## Architecture
```
User Input (main.py)
      ↓
Orchestrator
  ├── Router        → keyword scoring + @agent manual override
  ├── SessionMemory → per-agent conversation history
  └── Agent Layer
        ├── ClaudeAgent  → Anthropic API
        ├── GPTAgent     → OpenAI API
        └── GeminiAgent  → Google AI API
```

---

## Features

- **Smart Routing** — keyword scoring sends each task to the right model
- **Manual Override** — prefix with `@claude`, `@gpt`, or `@gemini` to force a specific agent
- **Session Memory** — each agent remembers conversation history within a session
- **Graceful Degradation** — if one agent fails, the system keeps running

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
# Edit .env and add your API keys
```

**3. Run**
```bash
python main.py
```

---

## Usage
```
> write a Unity singleton for GameManager
[Router] Routed to claude (scores: C=2 GPT=0 Ge=0)

> @gpt write a Steam description for a roguelike
[Router] Manual override → gpt

> @all what are the best practices for indie game monetization
[Router] Manual override → all agents
```

---

## Project Structure
```
GameDevCrew/
├── agents/
│   ├── claude_agent.py    # Unity code & architecture
│   ├── gpt_agent.py       # Marketing & copywriting
│   └── gemini_agent.py    # Research & documentation
├── core/
│   ├── orchestrator.py    # Task routing + session memory
│   └── router.py          # Keyword scoring + @agent override
├── utils/
│   └── formatter.py       # Terminal output formatting
├── main.py                # CLI entry point
└── .env.example           # API key template
```

---

## Built By

**CipherJ** — ex-EA Shanghai (FIFA Mobile), indie game developer, AI tooling enthusiast.
YouTube: [GameDevCrew tutorials coming soon]
GitHub: [@CipherJ98](https://github.com/CipherJ98)