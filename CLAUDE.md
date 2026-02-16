# CLAUDE.md — Project rules for tools4zettelkasten

## Language

- All code, variable names, commit messages, documentation, and comments must be in **English**, regardless of the language used in user prompts.

## Development workflow

### 1. Requirements first

Before implementing a feature or significant change, write a requirements document and place it in the `requirements/` folder (e.g., `requirements/requirements_<feature_name>.md`). The requirements document should describe:

- What the feature does and why it is needed
- Acceptance criteria
- Affected files and modules
- Test plan

### 2. Implementation

- Follow existing code conventions and project structure.
- Configuration is managed via `python-dotenv` and `os.environ.get()` in `settings.py` — do not introduce module-level mutable state or `exec()`-based settings.

### 3. Testing

- Every feature or bug fix must include **automated tests** added to the test suite in `tests/`.
- New tests must be integrated into the existing test suite so that `pytest tests/` discovers and runs them automatically — never leave tests as standalone scripts outside the suite.
- Before committing, run the **full test suite** to check for regressions:
  ```
  source venv/bin/activate && python -m pytest tests/ -v
  ```
- All tests must pass before a commit is created.

### 4. Documentation

- Update `README.rst` when adding new features, commands, or user-facing changes.
- Keep the README in sync with the actual state of the software.

### 5. Commits

- Write concise, meaningful commit messages in English.
- Summarize the "why", not just the "what".

## Project structure

- `tools4zettelkasten/` — main package (CLI, Flask views, MCP server, RAG, settings)
- `tests/` — automated test suite
- `requirements/` — requirements documents for features
- `.env` / `.env.example` — configuration (`.env` is gitignored)
- `README.rst` — user-facing documentation
