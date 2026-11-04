# Requirements: Collection ("shopping cart") and PDF/Markdown export

**Component:** Flask web UI (`tools4zettelkasten/flask_views.py`, templates,
static JS)
**Type:** Feature
**Created:** 2026-11-04

## What and why

The web UI (`start`) is used to browse the Zettelkasten. What is missing is a
way to take an *excerpt* of the Zettelkasten out of the tool for further
processing: as a PDF for reading and annotating away from the screen, or as a
single Markdown file to feed into Pandoc, Word or a blog post.

The Zettelkasten stores a train of thoughts, not a document. Turning a train of
thoughts into a linear document requires a step in between: picking the notes,
putting them in the order the argument needs, and only then exporting. This
feature adds that step as a **collection** — the user adds notes while
browsing, reviews and reorders them on a dedicated page, and exports the
result.

### Export technology decision

Notes contain MathJax formulas (`pymdownx.arithmatex` with `generic: True`),
Pygments syntax highlighting and images. A server-side PDF renderer such as
WeasyPrint does not execute JavaScript, so MathJax formulas would be lost;
Pandoc would handle them but requires a LaTeX installation.

This feature therefore produces PDF through a **print view**: a single HTML
document containing all selected notes, with a print stylesheet, which the
browser turns into a PDF via "Print → Save as PDF". This keeps full fidelity
(formulas, highlighting, images) and adds no dependency. Server-side PDF
rendering as an optional extra remains possible later; see
"Out of scope" below.

### State decision

The collection lives in the browser's `localStorage`, not in the Flask
`session`:

- The session is a cookie limited to ~4 KB; filenames are ~60 characters, so a
  collection of more than roughly 50 notes would not fit.
- `READ_ONLY` deployments (VPS mirror, see
  `requirements_read_only_web_ui.md`) may be read by several clients; a
  browser-local collection needs no server state at all.
- The collection survives server restarts.

The ordered list of filenames is sent to the server only at export time, by
`POST`.

## Acceptance criteria

### Collection state and shared JavaScript

1. A new static file `flask_frontend/static/js/collection.js` holds the
   collection logic. It stores the collection in `localStorage` under the key
   `t4z_collection` as a JSON array of filenames, preserving insertion order.
2. The file exposes functions to add, remove, toggle, reorder (move one
   position up/down), clear and read the collection, and it keeps a counter
   badge in sync on every page that includes it.
3. Corrupt or unparsable `localStorage` content is treated as an empty
   collection and overwritten on the next change; it must not break the page.
4. Adding a filename that is already in the collection does not create a
   duplicate and does not change its position.

### Start page (note list)

5. Each row of the list on `startpage.html` gets an add/remove toggle control
   for that note. The control reflects the current state ("in collection" vs.
   "add").
6. Each row carries the note's ordering as a `data-ordering` attribute (derived
   server-side via `handle_filenames.get_filename_components`) and its filename
   as a `data-filename` attribute.
7. Each row that has descendants offers a second control "add subtree", which
   adds the note **and all of its descendants** in the hierarchical order of
   the displayed list. A note's descendants are the entries whose ordering
   extends the note's ordering by at least one further level.
8. The page shows a collection badge with the current number of notes, linking
   to `/collection`.

### Note view

9. `mainpage.html` gets a toggle button in the existing `nav-footer` that adds
   the displayed note to the collection or removes it again, labelled according
   to the current state.
10. The keyboard shortcut `s` toggles the current note in the collection, `c`
    navigates to `/collection`. Both respect the existing guard that ignores
    key presses inside `INPUT`/`TEXTAREA` elements. The existing shortcuts
    (arrow keys, `l`, `e`) keep working unchanged.
11. The keyboard hint line mentions the new shortcuts.

### Collection page

12. New route `GET /collection` renders `collection.html`. The list of notes is
    rendered client-side from `localStorage`; the displayed title per note is
    derived from the filename (ordering and ID stripped, underscores replaced
    by spaces).
13. Each entry offers: move up, move down, remove. The page offers "clear all"
    and shows the number of notes.
14. With an empty collection the page shows an explanatory empty state instead
    of the export controls.
15. The page offers these export options, which are submitted with the export
    request:
    - `title` — free text for the title page (empty: no title page)
    - `toc` — include a table of contents (default on)
    - `page_breaks` — start each note on a new page (default on)
    - `show_sources` — print the filename of each note below its title
      (default on)
    - `demote_headings` — shift each note's headings down one level
      (default off)
16. Two export buttons submit the ordered filenames and the options:
    "Print / Save as PDF" to `/collection/print` and "Download Markdown" to
    `/collection/markdown`. Both submit by `POST` (a collection of many notes
    exceeds practical URL length limits).

### Print view

17. New route `POST /collection/print` renders `collection_print.html`
    containing all submitted notes in the submitted order, each rendered with
    the same Markdown configuration and Pygments/MathJax setup as
    `show_md_file`.
18. The document contains `<base href="/">` so that relative image paths in the
    notes (`![...](images/x.png)`) resolve against the existing `/images/`
    route. All URLs generated by `url_for` remain correct.
19. Each note is wrapped in a container with the anchor
    `id="note-<filename without .md>"`.
20. Inside each note, links to other notes (`href="<name>.md"`) are rewritten
    to `href="#note-<name>"` when `<name>.md` is part of the collection;
    links to notes outside the collection are left pointing at the site.
21. With `page_breaks` enabled, every note except the first starts on a new
    page (`break-before: page`); images and figures are not split across pages
    (`break-inside: avoid`).
22. The print stylesheet hides all interactive controls (`@media print`), so
    the PDF contains only the title page, the table of contents and the notes.
23. The view has a button that triggers `window.print()`, and a way back to
    `/collection`.
24. With `toc` enabled, the table of contents lists the notes in order, each
    linking to its anchor. The entry text is the note's first level-1 heading,
    falling back to the filename-derived title.

### Markdown export

25. New route `POST /collection/markdown` returns the concatenated **sources**
    of the submitted notes in the submitted order as a download
    (`text/markdown`, `Content-Disposition: attachment`, filename derived from
    the title option or `collection.md`).
26. Notes are separated by a blank line, a horizontal rule and a blank line.
    With `show_sources` enabled, each note is preceded by an HTML comment
    naming its filename. With `title` set, the file starts with that title as a
    level-1 heading (without a rule after it). `demote_headings` shifts ATX
    headings down one level.

### Validation, security and read-only mode

27. Submitted filenames are validated against the actual list of filenames from
    the `PersistencyManager`. A request containing an unknown filename returns
    HTTP 400 and renders nothing. This also rejects path traversal attempts
    (e.g. `../../etc/passwd`).
28. A request with an empty list of filenames returns HTTP 400.
29. Both export routes work unchanged when `READ_ONLY=true`; they only read.
    The collection controls are available in read-only mode.
30. Configuration, if any is added, follows the existing pattern
    (`settings.py` / `os.environ.get()`).

### Image route (prerequisite)

31. `send_image` resolves `ZETTELKASTEN_IMAGES` to an absolute path. Flask's
    `send_from_directory` resolves a relative directory against the app root
    (the package directory) rather than the working directory, so the default
    `../zettelkasten/mycelium/images` and every other relative path currently
    yields HTTP 404 — in the note view as well as in the export. Without this
    the exported PDF cannot contain the images of the notes.

## Affected files

- `tools4zettelkasten/flask_views.py` — routes `/collection`,
  `/collection/print`, `/collection/markdown`; helpers for filename
  validation, note title extraction, heading demotion, link rewriting;
  absolute image directory in `send_image`
- `tools4zettelkasten/flask_frontend/static/js/collection.js` — new,
  collection state and UI wiring
- `tools4zettelkasten/flask_frontend/templates/collection.html` — new,
  collection page
- `tools4zettelkasten/flask_frontend/templates/collection_print.html` — new,
  print view incl. print stylesheet
- `tools4zettelkasten/flask_frontend/templates/startpage.html` — add controls,
  `data-ordering`/`data-filename`, badge, script include
- `tools4zettelkasten/flask_frontend/templates/mainpage.html` — toggle button,
  shortcuts `s`/`c`, keyboard hint, script include
- `README.rst` — document the collection and the export
- `tests/test_collection_export.py` — new tests
- `tests/test_flask_views.py` — tests for the image route

## Test plan

`tests/test_collection_export.py` defines `client` / `zettelkasten_dir`
fixtures in the style of `tests/test_flask_views.py`, with a parent note, a
child note (containing an image and a sub heading) and an unrelated sibling.
`localStorage` behaviour is not testable from Flask; the tests cover the
server-side contract.

- `GET /collection` returns 200 and includes `collection.js`.
- Start page contains an add control, `data-filename` and `data-ordering` for
  every note, and the collection badge.
- Note view contains the collection toggle button and the `s`/`c` shortcuts.
- `POST /collection/print` with two notes returns 200 and contains both notes'
  rendered content **in the submitted order** (also verified with the reversed
  order).
- Print view contains `<base href="/">` and an anchor per note.
- A link from one collected note to another collected note is rewritten to
  `#note-...`; a link to a note outside the collection is not.
- `page_breaks` on/off toggles the page-break rule; `toc` on/off toggles the
  table of contents; `title` adds the title page; `show_sources` adds the
  filename; `demote_headings` turns `<h1>` into `<h2>`.
- `POST /collection/print` with an unknown filename → 400; with
  `../../etc/passwd` → 400; with an empty list → 400.
- `POST /collection/markdown` returns the sources in order, with the
  `text/markdown` content type and an attachment disposition.
- Both export routes return 200 with `st.READ_ONLY = True`.
- The image route serves a file from an absolute `ZETTELKASTEN_IMAGES`
  directory and from a relative one (the latter fails without the fix).
- Full suite (`pytest tests/ -v`) stays green.

## Out of scope (possible later stages)

- **Server-side PDF rendering** as an optional extra
  (`pip install tools4zettelkasten[pdf]`), analogous to the `[mcp]` and
  `[rag]` extras, for automated exports from the CLI or the MCP server. This
  needs the MathJax problem solved (MathML conversion, or Pandoc) and images
  embedded as absolute file paths.
- **Named, persisted collections** — stored as JSON under
  `~/.tools4zettelkasten/`, or as a "collection note" inside the Zettelkasten
  that consists only of links and can be exported directly.
- **Drag & drop reordering** (e.g. SortableJS) in addition to the up/down
  controls.
- **Adding notes from the graph view and from the RAG chat results.**
- **An `export` CLI command and an MCP export tool.**
