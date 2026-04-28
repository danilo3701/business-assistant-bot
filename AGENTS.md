# AGENTS.md

## Scope
These instructions apply to the whole `business-assistant-bot` repository.

## Shared Rules
- Use `../AGENTS.md` as the global architecture and UX contract.
- Keep this file focused on repo-local behavior.

## Delivery Mode
- Single-developer flow.
- Always work directly in `main`.
- No feature branches unless explicitly requested.

## Autocommit Policy
- After successful implementation and verification, run:
  - `powershell -ExecutionPolicy Bypass -File ..\tools\ship-repo.ps1 -RepoPath .`
- Commit message can be auto-generated, or set explicitly with:
  - `-Message "fix: <short summary>"`
- Default behavior is commit + push to `origin/main`.

## Guardrails
- Do not commit secrets.
- If tests/checks are available, run them before shipping.
