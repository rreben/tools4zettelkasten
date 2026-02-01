# Requirements: Settings Command Refactoring

## Hintergrund

Der aktuelle `show`-Befehl zeigt Konfigurationsinformationen an, hat aber mehrere Probleme:
- Der Name `show` ist generisch und nicht selbsterklärend
- Die Version wird nicht angezeigt, obwohl der Hilfetext das verspricht
- Die Ausgabe ist unstrukturiert und schwer zu lesen
- Keine visuelle Hierarchie oder Farbcodierung
- Keine Validierung, ob die konfigurierten Pfade existieren

## Ziel

1. Umbenennung des Befehls von `show` zu `settings`
2. Strukturierte, farbige Ausgabe analog zu `format_rename_output`
3. Anzeige der Version (wie im Hilfetext versprochen)
4. Validierung der Pfade mit visueller Statusanzeige
5. Anzeige des Status der Environment-Variablen

## Betroffene Funktionen

### Aktuelle `show`-Funktion

Die `show`-Funktion (`cli.py`, Zeilen 296-321) zeigt folgende Informationen an:
- Working directories (ZETTELKASTEN, ZETTELKASTEN_INPUT)
- Flask configuration (TEMPLATE_FOLDER, STATIC_FOLDER, ZETTELKASTEN_IMAGES)
- Hierarchy link descriptions (DIRECT_SISTER_ZETTEL, DIRECT_DAUGHTER_ZETTEL)

**Aktueller Code:**
```python
@click.command(help='show version and settings')
def show():
    print()
    print('Here is the configuration')
    print('Working directories')
    print(
        'Path to the Zettelkasten: ',
        st.ZETTELKASTEN,
        ' can be set via ZETTELKASTEN environment variable')
    # ... weitere print-Anweisungen
```

**Aktuelle Ausgabe:**
```
Here is the configuration
Working directories
Path to the Zettelkasten:  ../zettelkasten/mycelium  can be set via ZETTELKASTEN environment variable
Path to the Zettelkasten input:  ../zettelkasten/input  can be set via ZETTELKASTEN_INPUT environment variable

Flask configuration
Path to templates:  flask_frontend/templates
Path to static files:  flask_frontend/static
Path to images for flask:  /Users/.../images  can be set via ZETTELKASTEN_IMAGES environment variable

What we write to automatically generated hierachy links
comment for sister Zettel:  train of thoughts
comment for daughter Zettel:  detail / digression
Built-in settings can be changed in the settings.py file
```

### Gewünschte Ausgabe

```
╔══════════════════════════════════════════════════════════════════╗
║                tools4zettelkasten v0.1.0                         ║
╠══════════════════════════════════════════════════════════════════╣
║  WORKING DIRECTORIES                                             ║
║    Zettelkasten:       ../zettelkasten/mycelium              ✓   ║
║    Input:              ../zettelkasten/input                 ✓   ║
║    Images:             /Users/.../images                     ✗   ║
╠══════════════════════════════════════════════════════════════════╣
║  FLASK CONFIGURATION                                             ║
║    Templates:          flask_frontend/templates              ✓   ║
║    Static files:       flask_frontend/static                 ✓   ║
╠══════════════════════════════════════════════════════════════════╣
║  HIERARCHY LINKS                                                 ║
║    Sister Zettel:      train of thoughts                         ║
║    Daughter Zettel:    detail / digression                       ║
╠══════════════════════════════════════════════════════════════════╣
║  ENVIRONMENT VARIABLES                                           ║
║    ZETTELKASTEN              ✓ set                               ║
║    ZETTELKASTEN_INPUT        ✗ not set (using default)           ║
║    ZETTELKASTEN_IMAGES       ✗ not set (using default)           ║
╚══════════════════════════════════════════════════════════════════╝
```

## Anforderungen

### REQ-1: Umbenennung des Befehls

Der Befehl soll von `show` zu `settings` umbenannt werden.

**Akzeptanzkriterien:**
- Der Befehlsname ist `settings`
- Der Hilfetext ist aktualisiert: "show version and current settings"
- Der alte Befehl `show` existiert nicht mehr
- Die Registrierung in `messages.add_command()` ist aktualisiert

### REQ-2: Version anzeigen

Die Version soll im Header der Ausgabe angezeigt werden.

**Akzeptanzkriterien:**
- Die Version wird aus `__version__` gelesen
- Die Version erscheint im Header der Box
- Format: "tools4zettelkasten v{version}"

### REQ-3: Strukturierte Box-Ausgabe

Die Ausgabe soll in einer formatierten Box mit Sektionen dargestellt werden.

**Akzeptanzkriterien:**
- Verwendung von Unicode-Box-Zeichen (╔, ═, ╗, ║, ╠, ╣, ╚, ╝)
- Farbige Ausgabe mit `colorama` (bereits importiert)
- Sektionen: Header, Working Directories, Flask Configuration, Hierarchy Links, Environment Variables
- Dynamische Box-Breite basierend auf dem längsten Inhalt

### REQ-4: Pfad-Validierung mit Statusanzeige

Alle konfigurierten Pfade sollen auf Existenz geprüft werden.

**Akzeptanzkriterien:**
- Jeder Pfad wird mit `os.path.isdir()` oder `os.path.exists()` geprüft
- Existierende Pfade: grünes ✓
- Nicht existierende Pfade: rotes ✗
- Die Prüfung erfolgt für:
  - ZETTELKASTEN
  - ZETTELKASTEN_INPUT
  - ZETTELKASTEN_IMAGES
  - TEMPLATE_FOLDER
  - STATIC_FOLDER

### REQ-5: Environment-Variablen Status

Der Status der Environment-Variablen soll angezeigt werden.

**Akzeptanzkriterien:**
- Für jede relevante Environment-Variable wird angezeigt:
  - ✓ set - wenn die Variable gesetzt ist
  - ✗ not set (using default) - wenn die Variable nicht gesetzt ist
- Relevante Variablen: ZETTELKASTEN, ZETTELKASTEN_INPUT, ZETTELKASTEN_IMAGES

### REQ-6: Hilfsfunktion für formatierte Ausgabe

Eine wiederverwendbare Hilfsfunktion für die Box-Formatierung soll erstellt werden.

**Akzeptanzkriterien:**
- Funktion `format_settings_output()` oder ähnlich
- Nimmt die Konfigurationsdaten als Parameter
- Gibt die formatierte Box aus
- Kann für Tests isoliert aufgerufen werden

---

## Testanforderungen

### Bestehende Tests

Alle 48 existierenden Tests müssen weiterhin bestehen.

### Neue Tests

#### TEST-1: test_settings_command_exists

**Beschreibung:** Prüft, dass der `settings`-Befehl existiert und aufrufbar ist.

```python
def test_settings_command_exists():
    """Test that settings command is registered"""
    from click.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(zt.cli.messages, ['settings'])
    assert result.exit_code == 0
```

#### TEST-2: test_settings_shows_version

**Beschreibung:** Prüft, dass die Version in der Ausgabe enthalten ist.

```python
def test_settings_shows_version(capsys, monkeypatch):
    """Test that settings displays version"""
    # Mock environment and paths
    monkeypatch.setattr('os.path.isdir', lambda x: True)

    zt.cli.settings.callback()

    captured = capsys.readouterr()
    assert zt.__version__ in captured.out
```

#### TEST-3: test_settings_shows_paths

**Beschreibung:** Prüft, dass alle Pfade in der Ausgabe enthalten sind.

```python
def test_settings_shows_paths(capsys, monkeypatch):
    """Test that settings displays all configured paths"""
    monkeypatch.setattr('os.path.isdir', lambda x: True)

    zt.cli.settings.callback()

    captured = capsys.readouterr()
    assert 'ZETTELKASTEN' in captured.out or 'Zettelkasten' in captured.out
```

#### TEST-4: test_settings_validates_existing_path

**Beschreibung:** Prüft, dass existierende Pfade mit ✓ markiert werden.

```python
def test_settings_validates_existing_path(capsys, monkeypatch):
    """Test that existing paths show checkmark"""
    monkeypatch.setattr('os.path.isdir', lambda x: True)

    zt.cli.settings.callback()

    captured = capsys.readouterr()
    assert '✓' in captured.out
```

#### TEST-5: test_settings_validates_missing_path

**Beschreibung:** Prüft, dass nicht existierende Pfade mit ✗ markiert werden.

```python
def test_settings_validates_missing_path(capsys, monkeypatch):
    """Test that missing paths show X mark"""
    monkeypatch.setattr('os.path.isdir', lambda x: False)

    zt.cli.settings.callback()

    captured = capsys.readouterr()
    assert '✗' in captured.out
```

#### TEST-6: test_settings_shows_env_var_status

**Beschreibung:** Prüft, dass der Status der Environment-Variablen angezeigt wird.

```python
def test_settings_shows_env_var_status(capsys, monkeypatch):
    """Test that environment variable status is shown"""
    monkeypatch.setattr('os.path.isdir', lambda x: True)
    monkeypatch.setenv('ZETTELKASTEN', '/some/path')

    zt.cli.settings.callback()

    captured = capsys.readouterr()
    assert 'ENVIRONMENT' in captured.out or 'Environment' in captured.out
```

#### TEST-7: test_show_command_removed

**Beschreibung:** Prüft, dass der alte `show`-Befehl nicht mehr existiert.

```python
def test_show_command_removed():
    """Test that old show command no longer exists"""
    from click.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(zt.cli.messages, ['show'])
    assert result.exit_code != 0  # Command should not be found
```

---

## Implementierungshinweise

### Dateien die geändert werden müssen

1. **`cli.py`:**
   - Funktion `show()` umbenennen zu `settings()`
   - Neue Formatierungsfunktion `format_settings_output()` hinzufügen
   - Hilfsunktion für Pfad-Validierung hinzufügen
   - `messages.add_command(show)` ändern zu `messages.add_command(settings)`

2. **`tests/test_cli.py`:**
   - Neue Tests für `settings`-Befehl hinzufügen

### Hilfsfunktionen

```python
def check_path_exists(path: str) -> bool:
    """Check if a path exists."""
    return path.isdir(path) or path.isfile(path)

def get_env_var_status(var_name: str) -> tuple[bool, str]:
    """Get environment variable status.

    Returns:
        Tuple of (is_set, display_value)
    """
    from os import environ
    try:
        value = environ[var_name]
        return (True, value)
    except KeyError:
        return (False, None)
```

### Farbschema

| Element | Farbe |
|---------|-------|
| Box-Rahmen | Cyan |
| Header/Titel | Cyan + Bold |
| Sektions-Überschriften | White + Bold |
| Werte | White |
| ✓ (Pfad existiert) | Green |
| ✗ (Pfad fehlt) | Red |
| ✓ set | Green |
| ✗ not set | Yellow |

### Reihenfolge der Implementierung

1. Neue Formatierungsfunktion `format_settings_output()` erstellen
2. Hilfsfunktionen für Pfad-Validierung und Env-Var-Status erstellen
3. `show()` zu `settings()` umbenennen und neu implementieren
4. Tests schreiben
5. `messages.add_command()` aktualisieren
6. Alle Tests ausführen und validieren

---

## Testausführung

```bash
# Alle Tests ausführen
source venv/bin/activate && python -m pytest -v

# Nur neue Tests ausführen
source venv/bin/activate && python -m pytest -v -k "settings"

# Mit Coverage
source venv/bin/activate && python -m pytest --cov=tools4zettelkasten --cov-report=term-missing
```

## Erfolgskriterien

Die Implementierung gilt als erfolgreich, wenn:

1. Alle 48 bestehenden Tests grün sind
2. Alle neuen Tests (TEST-1 bis TEST-7) grün sind
3. Der Befehl `settings` die formatierte Box-Ausgabe zeigt
4. Die Version korrekt angezeigt wird
5. Pfade validiert werden mit ✓/✗ Anzeige
6. Der Status der Environment-Variablen angezeigt wird
7. Der alte `show`-Befehl nicht mehr existiert
