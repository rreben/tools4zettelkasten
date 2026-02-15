# Requirements: Integration des MCP-Servers in tools4zettelkasten

## Hintergrund

Der MCP-Server (`zettelkasten_mcp`) bietet eine Schnittstelle, um den Zettelkasten
via Claude (Desktop/Code) zu verwalten. Er ist derzeit ein separates Projekt unter
`../zettelkasten_mcp`, obwohl er:

- Keine eigene Geschäftslogik enthält, sondern alle Kernmodule aus `tools4zettelkasten`
  importiert (`handle_filenames`, `persistency`, `reorganize`, `analyse`)
- Einen `importlib`-Workaround nutzen muss, weil `__init__.py` mit `from .cli import *`
  den Namespace verschmutzt
- Settings (Pfade) separat per Environment-Variablen verwaltet, statt die zentrale
  `settings.py` zu nutzen

Der MCP-Server ist konzeptionell **die dritte Oberfläche** neben CLI und Flask-Web-UI.
Alle drei greifen auf dieselben Kernmodule zu. Die Verteilung auf zwei Projekte
führt zu doppelter Settings-Verwaltung und erschwerter Wartung.

## Ziel

Integration des MCP-Servers als Modul `mcp_server.py` innerhalb des Pakets
`tools4zettelkasten`, sodass:

1. Es nur noch **ein Projekt** gibt, das alle Oberflächen bereitstellt
2. Die zentrale `settings.py` auch für den MCP-Server gilt
3. Der `importlib`-Hack entfällt (direkte Imports innerhalb des Pakets)
4. Ein neuer CLI-Befehl `tools4zettelkasten mcp` den Server starten kann
5. `mcp[cli]` als optionale Dependency eingebunden wird

## Ist-Zustand

### Architektur `zettelkasten_mcp/server.py`

Der MCP-Server exponiert **12 Tools** via FastMCP:

| Kategorie | Tool | Beschreibung |
|-----------|------|-------------|
| Input | `list_input_files` | Dateien im Input-Ordner auflisten |
| Input | `preview_staging` | Geplante Umbenennungen anzeigen |
| Input | `stage_file` | Einzelne Datei umbenennen |
| Query | `get_zettel` | Einzelnen Zettel per ID/Dateiname abrufen |
| Query | `search_zettel` | Volltextsuche |
| Query | `list_zettel` | Zettel auflisten (mit Prefix-Filter) |
| Query | `get_statistics` | Statistiken zum Zettelkasten |
| Struktur | `get_links` | Links eines Zettels (ein-/ausgehend) |
| Struktur | `find_related` | Verwandte Zettel finden |
| Struktur | `analyze_structure` | Strukturanalyse mit Baumdarstellung |
| Reorg | `preview_reorganize` | Vorschau der Reorganisation |
| Reorg | `execute_reorganize` | Reorganisation durchführen |

### Import-Workaround im MCP-Server

```python
# Aktuell in zettelkasten_mcp/server.py
import importlib
hf = importlib.import_module("tools4zettelkasten.handle_filenames")
persistency_module = importlib.import_module("tools4zettelkasten.persistency")
ro = importlib.import_module("tools4zettelkasten.reorganize")
analyse = importlib.import_module("tools4zettelkasten.analyse")
```

Grund: `tools4zettelkasten/__init__.py` macht `from .cli import *`, was Click-Befehle
als Funktionen in den Paket-Namespace zieht. Das verursacht Namenskonflikte
(z.B. `reorganize` als Click-Command vs. als Modul).

### Settings-Dopplung

| Setting | tools4zettelkasten (settings.py) | zettelkasten_mcp (server.py) |
|---------|----------------------------------|------------------------------|
| Zettelkasten-Pfad | `st.ZETTELKASTEN` (relativ) | `ZETTELKASTEN_PATH` (env var) |
| Input-Pfad | `st.ZETTELKASTEN_INPUT` (relativ) | `ZETTELKASTEN_INPUT_PATH` (env var) |
| Images-Pfad | `st.ZETTELKASTEN_IMAGES` (absolut) | nicht verwendet |

Beide werden unabhängig voneinander aus Environment-Variablen bestückt.

## Anforderungen

### REQ-1: `__init__.py` bereinigen

Der Wildcard-Import `from .cli import *` muss entfernt werden, da er:
- Den Paket-Namespace mit Click-Commands verschmutzt
- Modulnamen wie `reorganize` überschattet
- Den `importlib`-Workaround im MCP-Server erzwingt

**Akzeptanzkriterien:**
- `__init__.py` exportiert nur `__version__` und `ZettelkastenTools`
- Alle Wildcard-Imports (`from .xyz import *`) werden entfernt
- Der Entry-Point `tools4zettelkasten:ZettelkastenTools.run` funktioniert weiterhin
- Alle bestehenden Tests sind grün

**Neuer `__init__.py`:**
```python
from ._version import __version__
from .app import ZettelkastenTools
```

**Risiko-Analyse:** Externe Nutzer, die `from tools4zettelkasten import create_Note`
o.ä. nutzen, müssten auf `from tools4zettelkasten.handle_filenames import create_Note`
umstellen. Da das Paket primär als CLI/Server genutzt wird und nicht als Library
veröffentlicht ist, ist dieses Risiko gering. Die Tests sollten zeigen, ob interne
Nutzung betroffen ist.

### REQ-2: MCP-Server-Modul anlegen

Eine neue Datei `tools4zettelkasten/mcp_server.py` erstellen, die den gesamten
Inhalt von `zettelkasten_mcp/server.py` übernimmt, aber mit direkten Imports.

**Akzeptanzkriterien:**
- Alle 12 MCP-Tools sind funktional identisch zum bestehenden Server
- Imports erfolgen direkt statt via `importlib`:
  ```python
  from . import handle_filenames as hf
  from .persistency import PersistencyManager
  from . import reorganize as ro
  from . import analyse
  from . import settings as st
  ```
- Pfade werden aus `settings.py` gelesen (nach `overwrite_settings()`),
  nicht aus eigenen Environment-Variablen
- Die `main()`-Funktion startet den Server via `mcp.run()`

### REQ-3: Settings-Logik zentralisieren und für MCP nutzen

Die Funktionen `overwrite_setting()`, `overwrite_settings()` und `check_directories()`
werden von `cli.py` nach `settings.py` verschoben. So kann jede Oberfläche (CLI,
Flask, MCP) sie direkt aus dem Settings-Modul aufrufen, ohne `cli.py` importieren
zu müssen.

Der MCP-Server nutzt die zentrale `settings.py`, wobei Environment-Variablen
diese wie gewohnt überschreiben.

**Akzeptanzkriterien:**
- `overwrite_setting()` und `overwrite_settings()` liegen in `settings.py`
- `check_directories()` liegt in `settings.py`
- `cli.py` importiert diese Funktionen aus `settings.py` statt sie selbst zu definieren
- `mcp_server.py` nutzt `st.ZETTELKASTEN` und `st.ZETTELKASTEN_INPUT` aus `settings.py`
- Vor der Server-Initialisierung wird `overwrite_settings()` aus `settings.py` aufgerufen
- Kein eigenes Env-Var-Parsing im MCP-Server
- Die `TOOLS4ZETTELKASTEN_PATH`- und `PYTHONPATH`-Variablen entfallen in der
  Claude-Konfiguration, da der Server jetzt Teil des Pakets ist

**Verschiebung aus `cli.py` nach `settings.py`:**

```python
# settings.py — neue Funktionen (verschoben aus cli.py)
import os
import logging

logger = logging.getLogger(__name__)

def overwrite_setting(environment_variable: str):
    """Overwrite a setting with the value of an environment variable."""
    value = os.environ.get(environment_variable)
    if value:
        globals()[environment_variable] = value
    else:
        logger.info(
            f"{environment_variable} not set in environment, "
            "using built-in default."
        )

def overwrite_settings():
    """Apply environment variable overrides to all settings."""
    overwrite_setting('ZETTELKASTEN')
    overwrite_setting('ZETTELKASTEN_INPUT')
    overwrite_setting('ZETTELKASTEN_IMAGES')

def check_directories(strict: bool = True):
    """Validate that configured directories exist.

    Args:
        strict: If True, exit on missing directory (CLI-Modus).
                If False, log warnings only (MCP-Server-Modus).
    """
    for name, path in [
        ('ZETTELKASTEN', ZETTELKASTEN),
        ('ZETTELKASTEN_INPUT', ZETTELKASTEN_INPUT),
        ('ZETTELKASTEN_IMAGES', ZETTELKASTEN_IMAGES),
    ]:
        if not os.path.isdir(path):
            msg = f"{path} is not a directory, please set {name} to a valid directory."
            if strict:
                print(msg)
                exit(1)
            else:
                logger.warning(msg)
```

**Anpassung in `cli.py`:**

```python
# cli.py — Import statt eigener Definition
from . import settings as st

# In der messages()-Group:
@click.group()
def messages():
    show_banner()
    init(autoreset=True)
    print('Initializing of tools4zettelkasten ...')
    st.overwrite_settings()
    st.check_directories(strict=True)
```

**Hinweis:** Die aktuelle `overwrite_setting()` in `cli.py` nutzt `exec()` für
die Zuweisung. In `settings.py` kann stattdessen `globals()[var] = value`
verwendet werden, was sicherer und lesbarer ist.

### REQ-4: Neuer CLI-Befehl `mcp`

Ein neuer Click-Befehl zum Starten des MCP-Servers.

**Akzeptanzkriterien:**
- `tools4zettelkasten mcp` startet den MCP-Server
- Der Befehl ist in `messages.add_command()` registriert
- Hilfetext: "start MCP server for Claude integration"
- Bei fehlendem `mcp`-Paket: klare Fehlermeldung mit Installationshinweis

**Code-Entwurf:**
```python
@click.command(help='start MCP server for Claude integration')
def mcp():
    try:
        from . import mcp_server
        mcp_server.run_server()
    except ImportError:
        print(Fore.RED + "MCP dependencies not installed.")
        print("Install with: pip install 'tools4zettelkasten[mcp]'")
```

### REQ-5: Optionale MCP-Dependency

`mcp[cli]` als optionale Dependency, damit das Paket auch ohne MCP-Support
installierbar bleibt.

**Akzeptanzkriterien:**
- `setup.py` erhält `extras_require={'mcp': ['mcp[cli]>=1.0.0']}`
- Installation mit MCP: `pip install tools4zettelkasten[mcp]`
- Ohne MCP: alle bestehenden Features funktionieren unverändert
- Der Import von `mcp` ist in `mcp_server.py` guard-protected:
  ```python
  from mcp.server.fastmcp import FastMCP  # Nur bei installiertem mcp-Paket
  ```

### REQ-6: Claude-Desktop-Konfiguration aktualisieren

Die `claude_desktop_config.json` muss angepasst werden, damit sie auf den
integrierten Server zeigt.

**Aktuelle Konfiguration:**
```json
{
  "mcpServers": {
    "zettelkasten": {
      "command": "/Users/.../zettelkasten_mcp/venv/bin/python",
      "args": ["-m", "zettelkasten_mcp"],
      "env": {
        "PYTHONPATH": "/Users/.../tools4zettelkasten",
        "TOOLS4ZETTELKASTEN_PATH": "/Users/.../tools4zettelkasten",
        "ZETTELKASTEN": "/Users/.../zettelkasten/mycelium",
        "ZETTELKASTEN_INPUT": "/Users/.../zettelkasten/input"
      }
    }
  }
}
```

**Neue Konfiguration:**
```json
{
  "mcpServers": {
    "zettelkasten": {
      "command": "/Users/.../tools4zettelkasten/venv/bin/python",
      "args": ["-m", "tools4zettelkasten.mcp_server"],
      "env": {
        "ZETTELKASTEN": "/Users/.../zettelkasten/mycelium",
        "ZETTELKASTEN_INPUT": "/Users/.../zettelkasten/input"
      }
    }
  }
}
```

**Akzeptanzkriterien:**
- `TOOLS4ZETTELKASTEN_PATH` und `PYTHONPATH` sind nicht mehr nötig
- `command` zeigt auf die venv von tools4zettelkasten
- `args` nutzt `-m tools4zettelkasten.mcp_server`
- Nur noch die Zettelkasten-Pfade als Env-Vars nötig

### REQ-7: `__main__.py` für MCP-Server

Damit `python -m tools4zettelkasten.mcp_server` funktioniert, braucht das
MCP-Server-Modul eine aufrufbare `run_server()`-Funktion und eine
`__main__`-Logik am Ende der Datei.

**Akzeptanzkriterien:**
- `python -m tools4zettelkasten.mcp_server` startet den Server
- Die Settings werden vor dem Start initialisiert (Environment-Variablen
  werden angewendet)
- Die Verzeichnisse werden geprüft (mit Warnungen, ohne Abbruch)
- Fehlermeldung bei fehlender MCP-Dependency

**Code-Entwurf am Ende von `mcp_server.py`:**
```python
def run_server():
    """Initialize settings and run the MCP server."""
    from . import settings as st
    st.overwrite_settings()
    st.check_directories(strict=False)
    mcp.run()

if __name__ == "__main__":
    run_server()
```

### REQ-8: `check_directories()` beim MCP-Start

Der MCP-Server soll beim Start die konfigurierten Verzeichnisse prüfen.
Anders als die CLI darf der Server aber **nicht abbrechen**, da er als
Hintergrundprozess von Claude gestartet wird. Stattdessen werden Warnungen
geloggt.

**Akzeptanzkriterien:**
- `check_directories(strict=False)` wird in `run_server()` aufgerufen
- Bei fehlenden Verzeichnissen: `logger.warning()` statt `exit(1)`
- Der Server startet auch bei fehlenden Verzeichnissen (Tools liefern
  dann aussagekräftige Fehlermeldungen beim Aufruf)
- `check_directories()` akzeptiert einen Parameter `strict` (siehe REQ-3)
- CLI nutzt `strict=True` (bestehenes Verhalten bleibt erhalten)
- MCP nutzt `strict=False` (nur Warnungen)

---

## Testanforderungen

### Bestehende Tests

Alle existierenden Tests müssen weiterhin bestehen. Die Bereinigung von
`__init__.py` (REQ-1) ist der kritischste Schritt — Tests zeigen sofort,
ob interne Imports betroffen sind.

### Neue Testdatei: `tests/test_mcp_server.py`

Alle MCP-spezifischen Tests werden in einer eigenen Datei gesammelt.
Dies stellt sicher, dass sie als Teil der regulären Testsuite mit
`python -m pytest` ausgeführt werden und künftige Regressionen auffangen.

#### TEST-1: test_init_does_not_export_cli_commands

**Beschreibung:** Prüft, dass `__init__.py` keine Click-Commands exportiert.
Verhindert Regressionen von REQ-1.

```python
def test_init_does_not_export_cli_commands():
    """Test that __init__.py does not pollute namespace with CLI commands."""
    import tools4zettelkasten
    # Diese sollten NICHT direkt im Paket-Namespace sein:
    assert not hasattr(tools4zettelkasten, 'stage')
    assert not hasattr(tools4zettelkasten, 'reorganize')
    assert not hasattr(tools4zettelkasten, 'analyse')
```

#### TEST-2: test_mcp_server_module_exists

**Beschreibung:** Prüft, dass das MCP-Server-Modul existiert und importierbar ist.

```python
def test_mcp_server_module_exists():
    """Test that mcp_server module can be imported."""
    from tools4zettelkasten import mcp_server
    assert hasattr(mcp_server, 'run_server')
```

#### TEST-3: test_mcp_server_uses_settings

**Beschreibung:** Prüft, dass der MCP-Server die zentrale settings.py nutzt.

```python
def test_mcp_server_uses_settings(monkeypatch):
    """Test that MCP server reads paths from settings module."""
    import tools4zettelkasten.settings as st
    import tools4zettelkasten.mcp_server as mcp_srv

    monkeypatch.setattr(st, 'ZETTELKASTEN', '/test/mycelium')
    monkeypatch.setattr(st, 'ZETTELKASTEN_INPUT', '/test/input')

    manager = mcp_srv.get_zettelkasten_manager()
    assert str(manager.zettelkasten) == '/test/mycelium'

    input_manager = mcp_srv.get_input_manager()
    assert str(input_manager.zettelkasten) == '/test/input'
```

#### TEST-4: test_mcp_cli_command_exists

**Beschreibung:** Prüft, dass der `mcp`-Befehl registriert ist.

```python
def test_mcp_cli_command_exists():
    """Test that mcp command is registered in CLI."""
    from click.testing import CliRunner
    import tools4zettelkasten.cli as cli
    runner = CliRunner()
    result = runner.invoke(cli.messages, ['--help'])
    assert 'mcp' in result.output
```

#### TEST-5: test_mcp_tools_registered

**Beschreibung:** Prüft, dass alle 12 MCP-Tools registriert sind.

```python
def test_mcp_tools_registered():
    """Test that all MCP tools are registered."""
    from tools4zettelkasten.mcp_server import mcp

    expected_tools = [
        'list_input_files', 'preview_staging', 'stage_file',
        'get_zettel', 'search_zettel', 'list_zettel', 'get_statistics',
        'get_links', 'find_related', 'analyze_structure',
        'preview_reorganize', 'execute_reorganize'
    ]
    registered = [tool.name for tool in mcp.list_tools()]
    for tool_name in expected_tools:
        assert tool_name in registered, f"Tool {tool_name} not registered"
```

#### TEST-6: test_mcp_server_no_importlib

**Beschreibung:** Prüft, dass kein `importlib`-Workaround mehr verwendet wird.

```python
def test_mcp_server_no_importlib():
    """Test that mcp_server.py does not use importlib hack."""
    from pathlib import Path
    server_code = Path('tools4zettelkasten/mcp_server.py').read_text()
    assert 'importlib' not in server_code
```

#### TEST-7: test_overwrite_settings_in_settings_module

**Beschreibung:** Prüft, dass `overwrite_settings()` in `settings.py` liegt
und Environment-Variablen korrekt anwendet.

```python
def test_overwrite_settings_in_settings_module(monkeypatch):
    """Test that overwrite_settings lives in settings.py and works."""
    import tools4zettelkasten.settings as st
    assert hasattr(st, 'overwrite_settings')
    assert hasattr(st, 'overwrite_setting')

    monkeypatch.setenv('ZETTELKASTEN', '/custom/path')
    st.overwrite_settings()
    assert st.ZETTELKASTEN == '/custom/path'
```

#### TEST-8: test_check_directories_strict_mode

**Beschreibung:** Prüft, dass `check_directories(strict=True)` bei fehlenden
Verzeichnissen abbricht (bestehendes CLI-Verhalten).

```python
def test_check_directories_strict_mode(monkeypatch):
    """Test that check_directories in strict mode exits on missing dir."""
    import tools4zettelkasten.settings as st
    assert hasattr(st, 'check_directories')

    monkeypatch.setattr(st, 'ZETTELKASTEN', '/nonexistent/path')
    with pytest.raises(SystemExit):
        st.check_directories(strict=True)
```

#### TEST-9: test_check_directories_non_strict_mode

**Beschreibung:** Prüft, dass `check_directories(strict=False)` bei fehlenden
Verzeichnissen nur warnt, ohne abzubrechen (MCP-Verhalten).

```python
def test_check_directories_non_strict_mode(monkeypatch, caplog):
    """Test that check_directories in non-strict mode only warns."""
    import logging
    import tools4zettelkasten.settings as st

    monkeypatch.setattr(st, 'ZETTELKASTEN', '/nonexistent/path')
    with caplog.at_level(logging.WARNING):
        st.check_directories(strict=False)  # Soll NICHT abbrechen
    assert '/nonexistent/path' in caplog.text
```

---

## Betroffene Dateien

### Zu ändernde Dateien

| Datei | Änderung |
|-------|----------|
| `tools4zettelkasten/__init__.py` | Wildcard-Imports entfernen (REQ-1) |
| `tools4zettelkasten/settings.py` | `overwrite_setting()`, `overwrite_settings()`, `check_directories()` aufnehmen (REQ-3) |
| `tools4zettelkasten/cli.py` | Settings-Funktionen durch Import aus `settings.py` ersetzen, `mcp`-Befehl hinzufügen (REQ-3, REQ-4) |
| `setup.py` | `extras_require` mit `mcp` Option hinzufügen (REQ-5) |

### Neu zu erstellende Dateien

| Datei | Inhalt |
|-------|--------|
| `tools4zettelkasten/mcp_server.py` | MCP-Server mit 12 Tools, direkte Imports, Settings aus `settings.py` (REQ-2, REQ-7, REQ-8) |
| `tests/test_mcp_server.py` | Regressionstests TEST-1 bis TEST-9 |

### Externe Änderung (nach Validierung)

| Datei | Änderung |
|-------|----------|
| `~/Library/Application Support/Claude/claude_desktop_config.json` | Neuer Pfad und vereinfachte Env-Vars |

---

## Reihenfolge der Implementierung

1. **REQ-1: `__init__.py` bereinigen** — Basis für alle weiteren Schritte.
   Tests laufen lassen, um Auswirkungen zu erkennen und zu beheben.

2. **REQ-3: Settings-Logik zentralisieren** — `overwrite_setting()`,
   `overwrite_settings()` und `check_directories()` nach `settings.py`
   verschieben. `cli.py` anpassen (Import statt eigener Definition).
   Tests laufen lassen, um sicherzustellen, dass die CLI weiterhin funktioniert.

3. **REQ-5: Optionale MCP-Dependency** — `setup.py` erweitern, `pip install -e .[mcp]`

4. **REQ-2 + REQ-7 + REQ-8: MCP-Server-Modul erstellen** — `mcp_server.py` mit
   direkten Imports, Settings aus `settings.py`, `check_directories(strict=False)`

5. **REQ-4: CLI-Befehl hinzufügen** — `mcp`-Command in `cli.py`

6. **Tests schreiben und ausführen** — `tests/test_mcp_server.py` mit
   TEST-1 bis TEST-9. Alle bestehenden Tests müssen weiterhin grün sein.

7. **REQ-6: Claude-Konfiguration anpassen** — Manueller Schritt nach
   erfolgreicher Validierung

---

## Testausführung

```bash
# Alle Tests ausführen (bestehende + neue)
source venv/bin/activate && python -m pytest -v

# Nur MCP-Integrationstests ausführen
source venv/bin/activate && python -m pytest -v tests/test_mcp_server.py

# Nur Settings-Tests aus der neuen Datei
source venv/bin/activate && python -m pytest -v -k "overwrite_settings or check_directories"

# MCP-Server manuell testen
source venv/bin/activate && python -m tools4zettelkasten.mcp_server
```

## Erfolgskriterien

Die Implementierung gilt als erfolgreich, wenn:

1. Alle bestehenden Tests grün sind
2. Alle neuen Tests (TEST-1 bis TEST-9) in `tests/test_mcp_server.py` grün sind
3. `python -m tools4zettelkasten.mcp_server` den Server startet
4. Der Server in Claude Desktop/Code funktioniert (manuelle Validierung)
5. Alle 12 MCP-Tools identisch zum bisherigen Server funktionieren
6. `settings.py` die einzige Quelle für Konfiguration und Settings-Logik ist
7. `overwrite_settings()` und `check_directories()` in `settings.py` liegen
8. `check_directories(strict=False)` beim MCP-Start Warnungen loggt
9. `check_directories(strict=True)` beim CLI-Start wie bisher abbricht
10. Kein `importlib` mehr im Einsatz ist
11. Das separate `zettelkasten_mcp`-Projekt danach archiviert werden kann

## Getroffene Entscheidungen

1. **`overwrite_settings()` wird nach `settings.py` verschoben.**
   Die Settings-Logik gehört ins Settings-Modul, nicht in die CLI.
   Der `exec()`-Hack wird dabei durch `globals()[]` ersetzt.

2. **`check_directories()` wird beim MCP-Start genutzt.**
   Mit `strict=False` werden fehlende Verzeichnisse als Warnung geloggt,
   ohne den Server abzubrechen. Die CLI nutzt weiterhin `strict=True`.
