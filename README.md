# 🎮 GameDevCrew — Your AI Game Development Team

A multi-agent system where Claude, GPT-4o, and Gemini work as specialized teammates for indie game developers.

## Agents

| Agent | Role | Best For |
|-------|------|----------|
| **Claude** | Senior Dev | C# scripts, Unity architecture, debugging |
| **GPT-4o** | Copywriter | Steam descriptions, devlogs, marketing |
| **Gemini** | Researcher | Unity docs, asset recommendations, market research |

## Setup

```bash
# 1. Clone and install
pip install -r requirements.txt

# 2. Add your API keys
cp .env.example .env
# Edit .env with your keys

# 3. Run
python main.py
```

## Usage

```bash
# Interactive mode
python main.py

# Single task
python main.py "Write a Unity C# singleton for GameManager"
```

## Project Structure

```
gamedevcrew/
├── agents/
│   ├── claude_agent.py    # Code & architecture
│   ├── gpt_agent.py       # Copywriting & marketing
│   └── gemini_agent.py    # Research & docs
├── core/
│   ├── orchestrator.py    # Main controller
│   └── router.py          # Task routing logic
├── utils/
│   └── formatter.py       # Rich terminal output
└── main.py                # Entry point
```

## How Routing Works

The Router scores your task against keyword lists for each agent and sends it to the best match. If multiple agents score equally, all three run in parallel.

## Roadmap

- [ ] Memory: persist conversation history per session
- [ ] Unity Editor Plugin: call agents directly from Unity
- [ ] Web UI: simple browser interface
- [ ] Agent collaboration: Claude asks Gemini for docs before writing code
