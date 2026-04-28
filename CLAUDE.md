@../AGENTS.md

# CLAUDE.md - business-assistant-bot

## Adapter to shared rules
- Global contract: ../AGENTS.md
- This file stores only bot-local runtime notes

## Quick start
```bash
python bot.py
```

## Project card
- Architecture hint: single-entry script with separated handlers/services
- Stack baseline: Python + aiogram + SQLite + YandexGPT

## Quick runtime map
### /start -> Main Menu
- command: `/start`
- handlers: `handlers.py`

### Core features
- booking flow -> `handlers.py` + `database.py`
- AI responses -> `yandex_gpt.py`
- business data source -> `business_data.json`

## Local notes
- Keep only verified local facts (paths, handlers, edge cases)
- Do not duplicate full AGENTS.md here
