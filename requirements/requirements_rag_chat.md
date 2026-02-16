# Requirements: RAG-basierter Chat mit dem Zettelkasten

## Hintergrund

Der Zettelkasten enthält eine wachsende Sammlung von Konzepten und Ideen in Form
von Markdown-Dateien. Derzeit gibt es zwei Wege, Wissen im Zettelkasten zu finden:

1. **Volltextsuche** (über MCP-Server `search_zettel` oder manuell)
2. **Navigieren entlang der Links** zwischen Notizen

Beide Methoden erfordern, dass man bereits weiß, wonach man sucht oder wo man
anfangen soll. Was fehlt, ist die Möglichkeit, dem Zettelkasten eine offene Frage
zu stellen und eine Antwort zu erhalten, die auf den eigenen Notizen basiert —
mit Verweis auf die relevanten Quellen.

## Ziel

Ein RAG-System (Retrieval-Augmented Generation), das:

1. Alle Zettel als Vektoren in einer lokalen Datenbank speichert
2. Auf Fragen des Nutzers die relevantesten Zettel findet
3. Mit der OpenAI API (GPT) eine Antwort generiert, die auf diesen Zetteln basiert
4. Die Quell-Zettel (ID, Titel, Ordering) transparent anzeigt
5. Inkrementell aktualisierbar ist (neue Zettel, geänderte Zettel)
6. **Kompatibel mit `reorganize`** ist — ein Reorganize darf kein unnötiges
   Re-Embedding auslösen

## Ist-Zustand

### Architektur

Der Zettelkasten wird über drei Oberflächen bedient:

- **CLI** (`python -m tools4zettelkasten`) — stage, reorganize, analyse, settings
- **Flask-Web-UI** — Listenansicht, Einzelansicht, Editor, Graph
- **MCP-Server** — 12 Tools für Claude Desktop/Code

Alle drei nutzen die Kernmodule `handle_filenames.py`, `persistency.py`,
`reorganize.py`, `analyse.py` und `settings.py`.

### Dateistruktur eines Zettels

```
[ordering]_[base_filename]_[id].md
```

- **Ordering**: Hierarchische Nummerierung (z.B. `01_09`, `01_09_01`)
- **Base Filename**: Sprechender Titel (z.B. `From_note_taking_to_note_making`)
- **ID**: 9-stelliger Hex-String (z.B. `1b6058a3a`) — **stabil und einzigartig**

### Was `reorganize` verändert

Der Befehl `reorganize` kanonisiert die alphanumerische Nummerierung:

```
01_12a_How_to_integrate_e0d27e3ad.md  ->  01_13_How_to_integrate_e0d27e3ad.md
01_12b_Working_with_de036a6bd.md      ->  01_14_Working_with_de036a6bd.md
```

Dabei ändern sich:
- **Ordering** im Dateinamen (kanonisiert)
- **Dateinamen** (weil Ordering sich ändert)
- **Link-Ziele im Inhalt** (werden automatisch auf neue Dateinamen korrigiert)

Dabei bleibt stabil:
- **ID** — ändert sich nie
- **Base Filename** — ändert sich nie
- **Inhaltlicher Text** — ändert sich nicht (nur Link-URLs werden umgeschrieben)

### Konsequenz für RAG

Wenn ein Content-Hash naiv über den gesamten Dateiinhalt berechnet wird, würde
ein `reorganize` dazu führen, dass alle Zettel mit umgeschriebenen Links als
"geändert" erkannt werden. Das würde unnötiges Re-Embedding auslösen, obwohl
der semantische Inhalt unverändert ist.

**Lösung**: Content-Hash wird über normalisierten Inhalt berechnet, in dem
Link-Dateinamen durch ihre IDs ersetzt werden (siehe REQ-3).

---

## Anforderungen

### REQ-1: Vektor-Datenbank mit ChromaDB

ChromaDB wird als eingebettete Vektor-Datenbank verwendet. Sie speichert die
Vektoren persistent auf der lokalen Festplatte.

**Begründung der Wahl:**
- Eingebettet (kein separater Server nötig)
- Python-nativ (passt zum bestehenden Stack)
- Persistiert auf Disk
- Unterstützt Metadaten-Filterung
- Leichtgewichtig für persönliche Zettelkasten-Größe

**Akzeptanzkriterien:**
- ChromaDB-Collection `zettelkasten` wird angelegt
- Speicherort: konfigurierbar über `settings.py` (Default: `~/.tools4zettelkasten/chroma_db`)
- Die Zettel-**ID** (9-Zeichen Hex) ist der Primary Key (`id`) in ChromaDB
- Pro Zettel werden folgende **Metadaten** gespeichert:
  - `filename`: aktueller Dateiname
  - `ordering`: aktuelle hierarchische Nummerierung
  - `title`: Titel aus dem Markdown-Header (`# ...`)
  - `content_hash`: Hash des normalisierten Inhalts (siehe REQ-3)
- Der vollständige Zettel-Text wird als `document` gespeichert

### REQ-2: Embedding-Modell

Für die Vektorisierung wird ein lokales Embedding-Modell aus der
`sentence-transformers`-Bibliothek verwendet.

**Modell**: `paraphrase-multilingual-MiniLM-L12-v2`

**Begründung der Wahl:**
- Kostenlos, lokal, keine API-Keys nötig
- Gute multilinguale Unterstützung (Zettelkasten enthält Deutsch und Englisch)
- 384 Dimensionen — kompakt und schnell
- Ausreichende Qualität für persönlichen Zettelkasten

**Akzeptanzkriterien:**
- Das Modell wird beim ersten `vectorize`-Aufruf automatisch heruntergeladen
- Embedding-Funktion ist als eigene Klasse gekapselt (für späteren Austausch,
  z.B. gegen Voyage AI)
- ChromaDB wird mit einer Custom Embedding Function konfiguriert

### REQ-3: Inhaltsnormalisierung für Content-Hash

Vor der Berechnung des Content-Hash wird der Markdown-Inhalt normalisiert,
damit `reorganize` kein unnötiges Re-Embedding auslöst.

**Normalisierung:**
Link-Dateinamen in Markdown-Links werden durch die Zettel-ID ersetzt:

```python
# Vorher (im Dateiinhalt):
[Beschreibung](01_12a_How_to_integrate_e0d27e3ad.md)

# Normalisiert (für Hash-Berechnung):
[Beschreibung](e0d27e3ad)
```

**Akzeptanzkriterien:**
- Funktion `normalize_content(content: str) -> str` in `rag.py`
- Regex ersetzt `[text](dateiname.md)` durch `[text](id)`, wobei die ID aus
  dem Dateinamen extrahiert wird
- Content-Hash wird als SHA-256 über den normalisierten Inhalt berechnet
- Nach einem `reorganize` ohne inhaltliche Änderungen meldet der Sync:
  0 Zettel neu embedded, n Zettel Metadaten aktualisiert

### REQ-4: Vektorisierungsmodul (`rag.py`)

Ein neues Modul `tools4zettelkasten/rag.py` kapselt die gesamte RAG-Logik.

**Klassen und Funktionen:**

```
ZettelkastenEmbedder
    - __init__(model_name)
    - embed_query(query: str) -> list[float]
    - embed_documents(documents: list[str]) -> list[list[float]]

VectorStore
    - __init__(chroma_path, embedder)
    - sync(persistency_manager) -> SyncResult
    - metadata_sync(persistency_manager) -> int
    - search(query: str, top_k: int) -> list[SearchResult]
    - get_stats() -> dict

normalize_content(content: str) -> str
compute_content_hash(content: str) -> str
```

**Akzeptanzkriterien:**
- `rag.py` liegt in `tools4zettelkasten/`
- Alle Imports aus dem bestehenden Paket erfolgen relativ
- `VectorStore.sync()` führt den inkrementellen Abgleich durch:
  1. Alle Markdown-Dateien aus dem PersistencyManager laden
  2. Für jede Datei: ID extrahieren, Inhalt normalisieren, Hash berechnen
  3. Mit ChromaDB vergleichen: neue IDs hinzufügen, geänderter Hash updaten,
     fehlende IDs entfernen
  4. Metadaten (filename, ordering, title) immer aktualisieren
- `VectorStore.search()` gibt `SearchResult`-Objekte zurück mit:
  - `zettel_id`: 9-Zeichen ID
  - `title`: Titel des Zettels
  - `ordering`: Aktuelle Nummerierung
  - `filename`: Aktueller Dateiname
  - `content`: Volltext des Zettels
  - `score`: Ähnlichkeitswert
- `SyncResult` enthält: `added`, `updated`, `deleted`, `unchanged`, `metadata_updated`

### REQ-5: CLI-Befehl `vectorize`

Ein neuer Click-Befehl zum Synchronisieren der Vektor-Datenbank.

**Akzeptanzkriterien:**
- `python -m tools4zettelkasten vectorize` führt einen inkrementellen Sync durch
- Ausgabe zeigt: Anzahl hinzugefügt, aktualisiert, gelöscht, unverändert
- Option `--full`: Löscht die gesamte Collection und baut sie neu auf
- Option `--stats`: Zeigt nur Statistiken der Vektor-Datenbank an
- Bei fehlendem `chromadb`- oder `sentence-transformers`-Paket: klare
  Fehlermeldung mit Installationshinweis

**Beispielausgabe:**
```
Syncing vector database...
  Added:    3 zettel
  Updated:  1 zettel
  Deleted:  0 zettel
  Unchanged: 142 zettel
  Metadata:  12 zettel updated (ordering/filename changes)
Done. 146 zettel in vector database.
```

### REQ-6: CLI-Befehl `chat`

Ein interaktiver Chat-Befehl in der Konsole.

**Multi-Turn-Konversation:**

Der Chat unterstützt von Beginn an Multi-Turn-Konversationen. Komplexe
Überlegungen erstrecken sich häufig über mehrere Fragen und Antworten.

- Der bisherige Konversationsverlauf (Fragen + Antworten) wird im Speicher
  gehalten und bei jeder neuen Anfrage an die OpenAI API mitgesendet
- Bei jeder neuen Frage wird ein frischer RAG-Retrieval durchgeführt, d.h.
  die Frage wird im Kontext der bisherigen Konversation interpretiert, aber
  die Vektor-Suche nutzt die aktuelle Frage
- Der Konversationsverlauf wird bei `quit`/`exit` verworfen

**Akzeptanzkriterien:**
- `python -m tools4zettelkasten chat` startet eine interaktive Chat-Sitzung
- Der Nutzer gibt eine Frage ein, das System:
  1. Sucht die Top-k relevantesten Zettel (Default: k=5)
  2. Baut einen Prompt mit dem Kontext der gefundenen Zettel
  3. Sendet den Prompt zusammen mit der bisherigen Konversation an die
     OpenAI API (GPT)
  4. Zeigt die Antwort an
  5. Zeigt die Quell-Zettel an (ID, Titel, Ordering)
  6. Speichert Frage und Antwort im Konversationsverlauf
- Folgefragen beziehen sich auf den bisherigen Kontext — das LLM kennt die
  vorherigen Fragen und Antworten
- Option `--top-k N`: Anzahl der abgerufenen Zettel (Default: 5)
- Eingabe von `quit` oder `exit` beendet den Chat
- `OPENAI_API_KEY` wird aus der Umgebungsvariable gelesen
- Bei fehlendem API-Key: klare Fehlermeldung

**Beispielinteraktion:**
```
Zettelkasten Chat (type 'quit' to exit)

You: Was sind die wichtigsten Prinzipien beim Erstellen von Zettelkasten-Notizen?

Zettelkasten: Basierend auf deinen Notizen sind die wichtigsten Prinzipien:

1. **Permanenz**: Notizen sollen nach der Aufnahme nicht mehr geändert werden
   und auch nach Jahren noch verständlich sein.
2. **Atomarität**: Eine Idee pro Notiz, damit sie isoliert nutzbar bleibt.
3. **Kontextfreiheit**: Jede Notiz muss für sich alleine Sinn ergeben.
4. **Eigenständige Formulierung**: Kein Copy-Paste, sondern Reformulierung
   in eigenen Worten.
5. **Verknüpfung**: Notizen werden in Gedankengängen angeordnet und durch
   Referenzen verbunden.

Quellen:
  [01_005] Schritt für Schritt Anleitung für Setup und Nutzung des Zettelkastens
  [01_008] How to integrate notes into the Zettelkasten
  [01_003] Quality of notes

You: Wie unterscheidet sich das vom Konzept des Scrapings bei Twyla Tharp?

Zettelkasten: Gute Frage — du bringst hier zwei verwandte aber unterschiedliche
Konzepte zusammen. In deinem Zettel über "Creative Habit" beschreibst du Scraping
als Startpunkt für eigene Kreativität...

Quellen:
  [01_012_02_4] Creative Habit über Scraping
  [01_005] Schritt für Schritt Anleitung für Setup und Nutzung des Zettelkastens

You: quit
Goodbye!
```

### REQ-7: Flask-Web-Chat-Interface

Eine Chat-Seite in der bestehenden Flask-Web-UI.

**Akzeptanzkriterien:**
- Neue Route `/chat` in `flask_views.py`
- Neues Template `chat.html` in `flask_frontend/templates/`
- Chat-Eingabefeld und Antwortbereich
- **Multi-Turn**: Der gesamte Konversationsverlauf wird angezeigt und in der
  Flask-Session gehalten. Folgefragen beziehen sich auf den bisherigen Kontext.
- Quell-Zettel werden als **klickbare Links** angezeigt, die zur
  Einzelansicht (`/<filename>`) führen
- Antworten werden als Markdown gerendert
- Button "Neue Konversation" zum Zurücksetzen des Verlaufs
- Startseite erhält einen Link zum Chat

### REQ-8: System-Prompt für das LLM

Der System-Prompt instruiert das LLM, wie es mit dem Zettelkasten-Kontext
umgehen soll.

**Akzeptanzkriterien:**
- System-Prompt ist in `rag.py` als Konstante definiert
- Der Prompt instruiert das LLM:
  - Antworte basierend auf den bereitgestellten Zettelkasten-Notizen
  - Wenn die Notizen keine Antwort hergeben, sage das ehrlich
  - Verweise auf die Quell-Zettel mit deren ID und Titel
  - Antworte in der Sprache der Frage (Deutsch oder Englisch)
  - Berücksichtige den bisherigen Konversationsverlauf bei Folgefragen
- Der Kontext wird als nummerierte Liste von Zetteln übergeben:
  ```
  [1] ID: e0d27e3ad | Titel: Schritt für Schritt Anleitung | Ordering: 01_005
  Inhalt des Zettels...

  [2] ID: 1b6058a3a | Titel: How to integrate notes | Ordering: 01_009
  Inhalt des Zettels...
  ```
- Die Konversationshistorie wird als `messages`-Array an die OpenAI API
  übergeben (System-Prompt + abwechselnd user/assistant Messages).
  Der RAG-Kontext (gefundene Zettel) wird bei jeder neuen Frage als
  aktualisierter Kontext in die User-Message eingebettet.

### REQ-9: Optionale RAG-Dependencies

Die RAG-Abhängigkeiten werden als optionale Extras in `setup.py` eingebunden.

**Akzeptanzkriterien:**
- `setup.py` erhält `extras_require` Eintrag `rag`:
  ```python
  extras_require={
      'mcp': ['mcp[cli]>=1.0.0'],
      'rag': [
          'chromadb>=0.4.0',
          'sentence-transformers>=2.2.0',
          'openai>=1.0.0',
      ],
  }
  ```
- Installation: `pip install 'tools4zettelkasten[rag]'`
- Ohne RAG: alle bestehenden Features funktionieren unverändert
- Bei fehlendem Paket: klare Fehlermeldung mit Installationshinweis

### REQ-10: Settings für RAG

Neue Konfigurationsvariablen in `settings.py`.

**Akzeptanzkriterien:**
- Neue Settings in `settings.py`:
  ```python
  # RAG settings
  CHROMA_DB_PATH = os.path.expanduser('~/.tools4zettelkasten/chroma_db')
  EMBEDDING_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'
  RAG_TOP_K = 5
  LLM_MODEL = 'gpt-4o'
  ```
- Alle per Umgebungsvariable überschreibbar
- `overwrite_settings()` wird um die neuen Variablen erweitert
- `settings`-Befehl zeigt auch RAG-Konfiguration an

---

## Testanforderungen

### Integration in die bestehende Testsuite

Die RAG-Tests werden in die bestehende Testsuite integriert und dienen als
Regressionstests für zukünftige Änderungen. Sie werden mit jedem
`python -m pytest` Aufruf automatisch mitausgeführt.

**Anforderungen:**
- Alle neuen Tests liegen in `tests/test_rag.py` und werden von pytest
  automatisch erkannt
- Die gesamte Testsuite (`python -m pytest`) muss nach der Implementierung
  erfolgreich durchlaufen — sowohl die bestehenden als auch die neuen Tests
- Tests, die externe APIs (OpenAI) oder große Modelle (sentence-transformers)
  benötigen, werden mit `@pytest.mark.skipif` dekoriert, falls die
  entsprechenden Pakete nicht installiert sind. So bleibt die Testsuite auch
  ohne `[rag]`-Dependencies lauffähig.
- Tests für reine Logik (Normalisierung, Content-Hash) haben keine externen
  Abhängigkeiten und laufen immer
- Die neuen Module dürfen keine bestehende Funktionalität beeinträchtigen

### Neue Testdatei: `tests/test_rag.py`

#### TEST-1: test_normalize_content_replaces_links

```python
def test_normalize_content_replaces_links():
    content = "See [note](01_12a_How_to_integrate_e0d27e3ad.md) for details."
    normalized = normalize_content(content)
    assert "e0d27e3ad" in normalized
    assert "01_12a" not in normalized
```

#### TEST-2: test_normalize_content_preserves_non_links

```python
def test_normalize_content_preserves_non_links():
    content = "# Titel\n\nEin normaler Absatz ohne Links."
    assert normalize_content(content) == content
```

#### TEST-3: test_normalize_content_handles_image_links

```python
def test_normalize_content_handles_image_links():
    content = "![Bild](images/screenshot.png)"
    assert normalize_content(content) == content
```

#### TEST-4: test_content_hash_stable_after_reorganize

```python
def test_content_hash_stable_after_reorganize():
    before = "See [note](01_12a_How_to_integrate_e0d27e3ad.md) for details."
    after = "See [note](01_13_How_to_integrate_e0d27e3ad.md) for details."
    assert compute_content_hash(before) == compute_content_hash(after)
```

#### TEST-5: test_content_hash_changes_on_real_edit

```python
def test_content_hash_changes_on_real_edit():
    original = "# Titel\n\nErster Absatz."
    edited = "# Titel\n\nErster Absatz mit Ergaenzung."
    assert compute_content_hash(original) != compute_content_hash(edited)
```

#### TEST-6: test_sync_adds_new_zettel

```python
def test_sync_adds_new_zettel(tmp_path):
    # Erstelle temporaere Zettel-Dateien
    # Fuehre sync durch
    # Pruefe, dass SyncResult.added > 0
```

#### TEST-7: test_sync_detects_unchanged_after_reorganize

```python
def test_sync_detects_unchanged_after_reorganize(tmp_path):
    # Erstelle Zettel, sync, aendere nur Dateinamen (wie reorganize)
    # Zweiter sync: added=0, updated=0, metadata_updated>0
```

#### TEST-8: test_search_returns_relevant_results

```python
def test_search_returns_relevant_results(tmp_path):
    # Erstelle Zettel zu verschiedenen Themen
    # Suche nach einem Thema
    # Pruefe, dass relevanter Zettel in Top-Ergebnissen
```

#### TEST-9: test_sync_removes_deleted_zettel

```python
def test_sync_removes_deleted_zettel(tmp_path):
    # Erstelle Zettel, sync, loesche Datei, erneuter sync
    # Pruefe, dass SyncResult.deleted > 0
```

#### TEST-10: test_vectorize_cli_command_exists

```python
def test_vectorize_cli_command_exists():
    from click.testing import CliRunner
    import tools4zettelkasten.cli as cli
    runner = CliRunner()
    result = runner.invoke(cli.messages, ['--help'])
    assert 'vectorize' in result.output
```

#### TEST-11: test_chat_cli_command_exists

```python
def test_chat_cli_command_exists():
    from click.testing import CliRunner
    import tools4zettelkasten.cli as cli
    runner = CliRunner()
    result = runner.invoke(cli.messages, ['--help'])
    assert 'chat' in result.output
```

---

## Betroffene Dateien

### Zu ändernde Dateien

| Datei | Änderung |
|-------|----------|
| `tools4zettelkasten/settings.py` | Neue RAG-Settings (REQ-10) |
| `tools4zettelkasten/cli.py` | Neue Befehle `vectorize` und `chat` (REQ-5, REQ-6) |
| `tools4zettelkasten/flask_views.py` | Neue Route `/chat` (REQ-7) |
| `setup.py` | Neue `extras_require` für `rag` (REQ-9) |

### Neu zu erstellende Dateien

| Datei | Inhalt |
|-------|--------|
| `tools4zettelkasten/rag.py` | RAG-Kernmodul: Embedder, VectorStore, Normalisierung (REQ-1 bis REQ-4, REQ-8) |
| `tools4zettelkasten/flask_frontend/templates/chat.html` | Web-Chat-Template (REQ-7) |
| `tests/test_rag.py` | Tests TEST-1 bis TEST-11 |

---

## Reihenfolge der Implementierung

1. **REQ-10: Settings** -- Neue Konfigurationsvariablen in `settings.py`.
   Basis für alle weiteren Schritte.

2. **REQ-9: Dependencies** -- `setup.py` um `rag` Extras erweitern,
   `pip install -e '.[rag]'`

3. **REQ-3: Normalisierung** -- `normalize_content()` und
   `compute_content_hash()` implementieren. Tests TEST-1 bis TEST-5.

4. **REQ-2 + REQ-1: Embedder und VectorStore** -- ChromaDB-Integration,
   Custom Embedding Function, `sync()` und `search()`. Tests TEST-6 bis TEST-9.

5. **REQ-8: System-Prompt** -- Prompt-Konstante und Kontext-Formatierung.

6. **REQ-5: CLI `vectorize`** -- Click-Befehl mit `--full` und `--stats`.
   Test TEST-10.

7. **REQ-6: CLI `chat`** -- Interaktiver Chat-Befehl. Test TEST-11.

8. **REQ-7: Flask-Chat** -- Web-Interface mit klickbaren Quellen.

---

## Erfolgskriterien

Die Implementierung gilt als erfolgreich, wenn:

1. Die **gesamte Testsuite** (`python -m pytest`) erfolgreich durchläuft —
   bestehende Tests und neue RAG-Tests gemeinsam, ohne Fehler
2. Alle neuen Tests (TEST-1 bis TEST-11) in `tests/test_rag.py` grün sind
   und als Regressionstests dauerhaft in der Testsuite verbleiben
3. `python -m tools4zettelkasten vectorize` alle Zettel vektorisiert
4. `python -m tools4zettelkasten vectorize` nach einem `reorganize` keine
   Re-Embeddings durchführt (nur Metadaten-Updates)
5. `python -m tools4zettelkasten chat` eine interaktive Chat-Sitzung startet
6. Antworten auf die Inhalte des Zettelkastens referenzieren
7. Quell-Zettel mit ID, Titel und Ordering angezeigt werden
8. Die Flask-Chat-Seite Quell-Zettel als klickbare Links anzeigt
9. Neue Zettel nach einem `vectorize`-Lauf im Chat auffindbar sind
10. Die RAG-Dependencies optional sind und das Paket ohne sie funktioniert

## Getroffene Entscheidungen

1. **Chunking**: Ein Zettel wird immer als ganzes Dokument embedded, nicht an
   `##`-Headern gesplittet. Zettel sind typischerweise kurz und atomar — das
   ist ein Kernprinzip des Zettelkastens.

2. **Multi-Turn von Anfang an**: Der Chat unterstützt direkt Multi-Turn-
   Konversationen. Komplexe Überlegungen erstrecken sich über mehrere Fragen
   und Antworten — Single-Turn wäre für den Anwendungsfall unbrauchbar.

3. **Embedding-Modell**: Start mit `paraphrase-multilingual-MiniLM-L12-v2`
   (lokal, kostenlos, multilingual). Die Architektur (REQ-2) kapselt den
   Embedder als austauschbare Klasse, sodass ein späterer Wechsel zu einem
   API-basierten Modell (z.B. Voyage AI) ohne Umbau möglich ist.

4. **LLM-Anbindung über OpenAI API**: Für die Textgenerierung wird die
   OpenAI API genutzt (`OPENAI_API_KEY`). Default-Modell: `gpt-4o`.
