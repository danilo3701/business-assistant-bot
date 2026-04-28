# AGENT.md

## Project
Business Assistant Bot (Telegram, aiogram 3).

## Current Architecture
- `bot.py` is the runtime entrypoint.
- Core handlers are in `handlers.py`.
- Config and env loading are in `config.py`.
- Persistence layer is in `database.py` (SQLite).
- AI integration is in `yandex_gpt.py`.
- Business catalog and FAQ data are in `business_data.json`.

## Primary Goal
Keep a simple local-first flow so the owner can quickly test bot behavior with a test token before deployment.

## Change Boundaries
- Prioritize changes inside:
  - `bot.py`
  - `handlers.py`
  - `config.py`
  - `database.py`
  - `yandex_gpt.py`
  - `business_data.json`
- Avoid broad refactors unless explicitly requested.

## Safety Checks Before Finish
- Run syntax check:
  - `python -m py_compile bot.py handlers.py config.py database.py yandex_gpt.py`
- Confirm `.env.example` still matches required runtime variables.

## How To Describe Tasks
When user reports issue or asks for UI/text change, describe request in this structure:
- Path by buttons:
  - example: `/start -> Main Menu -> Service List -> Booking`
- Current behavior (what is wrong now).
- Expected behavior (what should happen).
- UI requirements (bold text, order of blocks, emoji, button label changes).
- Done criteria (how user checks result in chat UI).

## How Assistant Should Respond
- First confirm understood navigation path and affected screen.
- Then propose 2-3 options for UX/text improvements when task is visual/textual.
- Ask only critical clarifying questions that change implementation.
- Provide concrete change plan:
  - which callbacks/screens are touched,
  - what text/button changes are made,
  - how to verify.

## Quick Runtime Map (for fast navigation)
- `Main menu`:
  - entry command: `/start`
  - core handlers: `handlers.py`
- `Client booking flow`:
  - service/date/time and contact capture in `handlers.py`
  - data storage in `database.py`
- `AI assistant answers`:
  - generation logic in `yandex_gpt.py`
  - prompt/business context from `business_data.json`
- `Admin commands`:
  - examples in README: `/today`, `/week`, `/stats`, `/export`
