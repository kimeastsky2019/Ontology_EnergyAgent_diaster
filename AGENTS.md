# Repository Guidelines

## Project Structure & Module Organization
- `server.py`/`server_cloud.py` provide FastMCP entrypoints; keep deployment helpers such as `data_scheduler.py` and `setup_server.sh` nearby.
- Feature-specific tools live in `tools/` by domain (time_series, modeling, dashboards, weather, climate, storage); align new modules with this taxonomy.
- Extended services reside in `api-server/`, `automl/`, `multi_mcp_system/`, and `mobile-app/`; reuse these shells when adding interfaces.
- Shared configuration is in `config/settings.py`, with sample data in `data/` and walkthroughs in `examples/`. Tests belong in the standalone runners and under `tests/`, which should mirror runtime packages.

## Build, Test, and Development Commands
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python server.py                      # start MCP server
python energy_agent_client.py         # run LangGraph client
python data_scheduler.py              # execute data scheduler
python -m pytest tests                # full pytest suite
pytest tests/test_weather_tools.py    # focused check
```

## Coding Style & Naming Conventions
Use 4-space indentation, snake_case functions, PascalCase classes, and UPPER_SNAKE constants. Auto-format with `black .` and `isort .`; validate critical paths with `mypy tools/ server.py`. Keep async patterns consistent with existing clients and document custom prompts or tool contracts with concise docstrings.

## Testing Guidelines
Pytest with `pytest-asyncio` is the standard harness. Mirror every new runtime module with `tests/test_<module>.py`, and supply fixtures for deterministic data. Pair pipeline or agent changes with an integration call that exercises `server.py` or `energy_agent_client.py`. Mock outbound APIs or use cached payloads so CI stays network-free.

## Commit & Pull Request Guidelines
Follow Conventional Commits (`feat:`, `fix:`, `chore:`) and keep subjects within 72 characters. PRs must include a summary, linked issue or context, verification notes (`pytest`, manual scenario), and visuals when dashboards or UI assets change. Surface edits to `config/settings.py`, deployment manifests (`render.yaml`, `railway.json`), or secrets in the description to plan rollouts.

## Security & Configuration Tips
Store credentials such as `OPENAI_API_KEY` and `OPENWEATHER_API_KEY` in environment variables or secret managers. When adding integrations, gate remote calls behind configuration flags and document any new env vars or IAM requirements. Verify that sensitive files stay out of version control (check `.gitignore` before committing).
