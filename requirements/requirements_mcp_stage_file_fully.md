# Requirements: MCP `stage_file` full staging (parity with CLI `stage --fully`)

**Component:** MCP server (`tools4zettelkasten/mcp_server.py`)
**Type:** Bugfix / behavior alignment with the CLI
**Created:** 2026-06-08

## What and why

The MCP tool `stage_file` only renamed an input file to its title-based base
name (e.g. `aaa.md` → `Architektur_einer_AgentenHierarchie.md`). It omitted the
**ID** and the **preliminary ordering**, so `list_input_files` kept reporting
`has_id: false` / `has_ordering: false`.

The CLI command `stage` (default `--fully`) performs three steps and produces a
fully convention-conformant name `0_0_{Title}_{id}.md`. The MCP server must
deliver the same result so that agent-driven staging matches the CLI.

A second defect in the same module: `preview_reorganize` and
`execute_reorganize` access the `Rename_command` dataclass via index
(`cmd[1]`/`cmd[2]`), which raises `TypeError: 'Rename_command' object is not
subscriptable`. These must use the attributes `cmd.old_filename` /
`cmd.new_filename`.

## Acceptance criteria

1. `stage_file` defaults to `fully=True`; `fully=False` reproduces the previous
   title-only rename.
2. Fresh input result matches `^0_0_[A-Za-z0-9_]+_[0-9a-f]{9}\.md$`.
3. After staging, `list_input_files` reports `has_id: true`,
   `has_ordering: true`, `ordering: "0_0"`.
4. Idempotency: re-staging an already valid name causes no change and returns
   `message: "No rename needed"`.
5. ID generation goes through `hf.generate_id` (via `ro.attach_missing_ids`) —
   no custom implementation.
6. The preliminary ordering is exactly `0_0`, sourced from
   `ro.attach_missing_orderings` (not duplicated/hardcoded).
7. No writes outside `st.ZETTELKASTEN_INPUT`.
8. `preview_reorganize` / `execute_reorganize` no longer use subscript access on
   `Rename_command`; attribute access is used instead.
9. `preview_staging` gains a `fully` parameter (default `True`) and previews the
   full target name with a `0_0` ordering and an `<id>` placeholder, plus a note
   that a new ID is generated at staging time (the ID is timestamp-seeded and
   cannot be predicted).

## Affected files

- `tools4zettelkasten/mcp_server.py` — extend `stage_file` (steps 2+3, `fully`
  param); add `stage_all`; fix `cmd[1]/cmd[2]` → attribute access.
- `tests/test_mcp_stage.py` (new) — unit tests.

## Test plan

- `stage_file` default → matches full pattern; old file gone, new file present.
- `stage_file(fully=False)` → title-only name.
- Idempotent re-stage → "No rename needed".
- File without markdown header → `success: False`.
- Umlaut transliteration (`# Über Ärger` → `Ueber_Aerger`).
- ID only matched against `^[0-9a-f]{9}$` (timestamp-seeded, non-deterministic).
- `preview_reorganize` runs without `TypeError` on input with missing ids.
- Full suite (`pytest tests/ -v`) stays green.
