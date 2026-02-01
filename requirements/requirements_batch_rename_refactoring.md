# Requirements: Batch Rename Refactoring

## Hintergrund

Aktuell muss der Nutzer bei der `reorganize`-Funktion jede einzelne Dateiumbenennung separat bestätigen. Im Gegensatz dazu funktioniert das Korrigieren von Links (`batch_replace`) mit einer einzigen Bestätigung für alle Änderungen. Diese Inkonsistenz führt zu einer schlechten User Experience, insbesondere bei größeren Zettelkästen mit vielen Umbenennungen.

## Ziel

Die `batch_rename`-Funktion soll analog zu `batch_replace` refaktoriert werden:
1. Einführung einer `Rename_command`-Klasse für konsistentes Command Pattern
2. Übersichtliche Anzeige aller geplanten Umbenennungen
3. Eine einzige Bestätigung für alle Umbenennungen
4. Beibehaltung der korrekten Reihenfolge der Umbenennungen

## Betroffene Funktionen

### `reorganize`-Funktion

Die `reorganize`-Funktion ruft `batch_rename` zweimal auf:
1. Für fehlende IDs (`attach_missing_ids`)
2. Für Hierarchie-Änderungen (`create_rename_commands`)

Zusätzlich wird `batch_replace` für Link-Korrekturen aufgerufen.

### `stage`-Funktion

Die `stage`-Funktion (`cli.py`, Zeilen 180-194) verwendet ebenfalls `batch_rename`:

```python
def stage(fully):
    persistencyManager = PersistencyManager(st.ZETTELKASTEN_INPUT)
    stg.process_files_from_input(persistencyManager)
    if fully:
        print('Searching for missing IDs')
        batch_rename(
            ro.attach_missing_ids(
                persistencyManager.get_list_of_filenames()),
            persistencyManager)
        print('Searching for missing orderingss')
        batch_rename(
            ro.attach_missing_orderings(
                persistencyManager.get_list_of_filenames()),
            persistencyManager)
```

**Auswirkungen auf `stage`:**

Die `stage`-Funktion profitiert automatisch vom Refactoring, da sie dieselben Funktionen verwendet:
- `attach_missing_ids()` → erster Batch
- `attach_missing_orderings()` → zweiter Batch

**Vorher (aktuelles Verhalten):**
```
Searching for missing IDs
Rename  file1.md  -->
file1_abc123def.md ?
Proceed? [y/N]: y
Rename  file2.md  -->
file2_def456ghi.md ?
Proceed? [y/N]: y
Searching for missing orderingss
Rename  file1_abc123def.md  -->
0_0_file1_abc123def.md ?
Proceed? [y/N]: y
...
```

**Nachher (nach Refactoring):**
```
Searching for missing IDs
╔════════════════════════════════════════════════════════════════╗
║                    Geplante Umbenennungen (2)                   ║
╠════════════════════════════════════════════════════════════════╣
║  1. file1.md                                                   ║
║     → file1_abc123def.md                                       ║
║  2. file2.md                                                   ║
║     → file2_def456ghi.md                                       ║
╚════════════════════════════════════════════════════════════════╝
Proceed? [y/N]: y

Searching for missing orderingss
╔════════════════════════════════════════════════════════════════╗
║                    Geplante Umbenennungen (2)                   ║
╠════════════════════════════════════════════════════════════════╣
║  1. file1_abc123def.md                                         ║
║     → 0_0_file1_abc123def.md                                   ║
║  2. file2_def456ghi.md                                         ║
║     → 0_0_file2_def456ghi.md                                   ║
╚════════════════════════════════════════════════════════════════╝
Proceed? [y/N]: y
```

**Verbesserungen für `stage`:**
- Statt N einzelne Bestätigungen pro Batch → eine Bestätigung pro Batch
- Bessere Übersicht über alle geplanten Änderungen
- Weniger Nutzerinteraktion erforderlich
- Konsistentes Verhalten mit `reorganize`

## Anforderungen

### REQ-1: Rename_command Dataclass

Eine neue Dataclass `Rename_command` soll in `cli.py` eingeführt werden:

```python
@dataclass()
class Rename_command(Command):
    old_filename: str
    new_filename: str
```

**Akzeptanzkriterien:**
- Die Klasse erbt von der bestehenden `Command`-Basisklasse
- Die Klasse enthält die Felder `old_filename` und `new_filename`
- Die Klasse ist als `@dataclass` implementiert

### REQ-2: Anpassung der Command-Generierung

Die Funktionen in `reorganize.py`, die Rename-Commands erzeugen, sollen `Rename_command`-Objekte zurückgeben:

Betroffene Funktionen:
- `attach_missing_ids()` (Zeile 146-184)
- `attach_missing_orderings()` (Zeile 133-143)
- `create_rename_commands()` (Zeile 471-482)

**Akzeptanzkriterien:**
- Alle genannten Funktionen geben `list[Rename_command]` zurück
- Die bisherige Listen-Struktur `['rename', old, new]` wird durch `Rename_command`-Objekte ersetzt

### REQ-3: Übersichtliche Anzeige der Umbenennungen

Vor der Bestätigung soll eine übersichtliche, formatierte Ausgabe aller geplanten Umbenennungen erfolgen.

**Akzeptanzkriterien:**
- Kopfzeile mit Anzahl der geplanten Umbenennungen
- Tabellarische oder nummerierte Darstellung
- Für jede Umbenennung: alter Dateiname → neuer Dateiname
- Visuelle Hervorhebung der Änderungen (z.B. durch Farbe oder Formatierung)
- Bei leerer Liste: Hinweis "Keine Umbenennungen erforderlich"

**Beispiel-Ausgabe:**
```
╔════════════════════════════════════════════════════════════════╗
║                    Geplante Umbenennungen (3)                   ║
╠════════════════════════════════════════════════════════════════╣
║  1. 1_5_another_Thought_2af216153.md                           ║
║     → 1_2_another_Thought_2af216153.md                         ║
║  2. 2_3_a_Thought_on_Second_Topic_176fb43ae.md                 ║
║     → 2_1_a_Thought_on_Second_Topic_176fb43ae.md               ║
║  3. no_ordering_abc123def.md                                   ║
║     → 0_0_no_ordering_abc123def.md                             ║
╚════════════════════════════════════════════════════════════════╝
```

### REQ-4: Batch-Bestätigung

Die Bestätigung soll analog zu `batch_replace` erfolgen: Eine einzige Bestätigung für alle Umbenennungen.

**Akzeptanzkriterien:**
- Nach der Anzeige aller Umbenennungen erscheint eine einzige Bestätigungsabfrage
- Bei "Ja": Alle Umbenennungen werden durchgeführt
- Bei "Nein": Keine Umbenennung wird durchgeführt
- Default-Wert bleibt `False` (wie bisher)

### REQ-5: Reihenfolge der Umbenennungen

Die Reihenfolge der Umbenennungen muss beibehalten werden, da die Hierarchie-Reorganisation eine bestimmte Reihenfolge erfordert.

**Akzeptanzkriterien:**
- Die Umbenennungen werden in der Reihenfolge ausgeführt, wie sie in der Command-Liste stehen
- Die Reihenfolge der Command-Generierung in `reorganize.py` bleibt unverändert
- Die Baumstruktur-basierte Generierung in `create_rename_commands()` behält ihre Ordnung bei

### REQ-6: Abwärtskompatibilität

Die Änderungen sollen keine bestehenden Funktionalitäten brechen.

**Akzeptanzkriterien:**
- Alle existierenden 41 Tests müssen weiterhin bestehen
- Die `stage`-Funktion, die ebenfalls `batch_rename` verwendet, funktioniert weiterhin
- Die `reorganize`-Funktion produziert dieselben Ergebnisse (nur die Interaktion ändert sich)

---

## Testanforderungen

### Bestehende Tests (müssen weiterhin bestehen)

Alle 41 existierenden Tests müssen nach dem Refactoring grün sein:

**test_reorganize.py:**
- `test_get_list_of_invalid_links`
- `test_attach_missing_orderings`
- `test_attach_missing_ids`
- `test_generate_tokenized_list`
- `test_corrections_elements`
- `test_corrections_elements_shrink`
- `test_generate_tree`
- `test_get_hierarchy_links`
- `test_reorganize_filenames`
- `test_create_rename_commands`
- `test_get_list_of_links_from_file`
- `test_generate_tokenized_list_with_alpha_in_middle`
- `test_reorganize_with_alpha_in_middle`
- `test_corrections_elements_with_alpha_keys`

**test_persistency.py:**
- `test_persistency_manager`
- `test_create_file`
- `test_is_file_existing`
- `test_rename_file`
- `test_list_of_filenames_from_directory`
- `test_is_text_file`
- `test_is_markdown_file`
- `test_file_content`
- `test_get_string_from_file_content`
- `test_overwrite_file_content`

**test_handle_filenames.py:**
- `test_trailing_spaces`
- `test_multiple_spaces_removed`
- `test_replace_spaces_with_underscores`
- `test_replace_umlaute`
- `test_remove_special_characters`
- `test_hash`
- `test_currentTimestamp`
- `test_get_filename_components`
- `test_create_Note`
- `test_is_valid_filename`
- `test_create_filename`
- `test_is_valid_ordering`

**test_stage.py:**
- `test_process_txt_file`
- `test_process_files_from_input`
- `test_process_files_from_input_with_error`
- `test_process_files_from_input_with_existing_id`

**test_app.py:**
- `test_app`

### Neue Tests

#### TEST-1: test_rename_command_dataclass

**Beschreibung:** Prüft, dass die `Rename_command`-Klasse korrekt funktioniert.

```python
def test_rename_command_dataclass():
    """Test Rename_command dataclass creation and attributes"""
    cmd = Rename_command(
        old_filename='old_file.md',
        new_filename='new_file.md'
    )
    assert cmd.old_filename == 'old_file.md'
    assert cmd.new_filename == 'new_file.md'
    assert isinstance(cmd, Command)
```

#### TEST-2: test_attach_missing_ids_returns_rename_commands

**Beschreibung:** Prüft, dass `attach_missing_ids()` eine Liste von `Rename_command`-Objekten zurückgibt.

```python
def test_attach_missing_ids_returns_rename_commands():
    """Test that attach_missing_ids returns Rename_command objects"""
    test_list = [
        '1_2_reframe_your_goal.md',  # missing ID
        '2_5_homebrew_41e5a496c.md'  # has ID
    ]
    command_list = zt.attach_missing_ids(test_list)
    assert len(command_list) == 1
    assert isinstance(command_list[0], zt.cli.Rename_command)
    assert command_list[0].old_filename == '1_2_reframe_your_goal.md'
    assert re.match(r'1_2_reframe_your_goal_[0-9a-f]{9}\.md$',
                    command_list[0].new_filename)
```

#### TEST-3: test_attach_missing_orderings_returns_rename_commands

**Beschreibung:** Prüft, dass `attach_missing_orderings()` eine Liste von `Rename_command`-Objekten zurückgibt.

```python
def test_attach_missing_orderings_returns_rename_commands():
    """Test that attach_missing_orderings returns Rename_command objects"""
    test_list = [
        'some_cloud_idea_43e5a488c.md',  # missing ordering
        '2_5_homebrew_41e5a496c.md'       # has ordering
    ]
    command_list = zt.attach_missing_orderings(test_list)
    assert len(command_list) == 1
    assert isinstance(command_list[0], zt.cli.Rename_command)
    assert command_list[0].old_filename == 'some_cloud_idea_43e5a488c.md'
    assert command_list[0].new_filename == '0_0_some_cloud_idea_43e5a488c.md'
```

#### TEST-4: test_create_rename_commands_returns_rename_command_objects

**Beschreibung:** Prüft, dass `create_rename_commands()` `Rename_command`-Objekte zurückgibt.

```python
def test_create_rename_commands_returns_rename_command_objects():
    """Test that create_rename_commands returns Rename_command objects"""
    potential_changes = [
        ['1_2', '1_5_another_Thought_2af216153.md'],
        ['2_1', '2_3_a_Thought_176fb43ae.md']
    ]
    command_list = zt.create_rename_commands(potential_changes)
    assert len(command_list) == 2
    for cmd in command_list:
        assert isinstance(cmd, zt.cli.Rename_command)
    assert command_list[0].old_filename == '1_5_another_Thought_2af216153.md'
    assert command_list[0].new_filename == '1_2_another_Thought_2af216153.md'
```

#### TEST-5: test_batch_rename_executes_all_commands

**Beschreibung:** Prüft, dass `batch_rename` alle Umbenennungen in der richtigen Reihenfolge durchführt.

```python
def test_batch_rename_executes_all_commands(tmp_path, mocker):
    """Test that batch_rename executes all rename commands in order"""
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()

    # Create test files
    (test_dir / "old1.md").write_text("content1")
    (test_dir / "old2.md").write_text("content2")
    (test_dir / "old3.md").write_text("content3")

    persistency_manager = zt.PersistencyManager(test_dir)

    commands = [
        zt.cli.Rename_command('old1.md', 'new1.md'),
        zt.cli.Rename_command('old2.md', 'new2.md'),
        zt.cli.Rename_command('old3.md', 'new3.md'),
    ]

    # Mock the prompt to return True
    mocker.patch('tools4zettelkasten.cli.prompt',
                 return_value={'proceed': True})

    zt.cli.batch_rename(commands, persistency_manager)

    # Verify all files were renamed
    assert (test_dir / "new1.md").exists()
    assert (test_dir / "new2.md").exists()
    assert (test_dir / "new3.md").exists()
    assert not (test_dir / "old1.md").exists()
    assert not (test_dir / "old2.md").exists()
    assert not (test_dir / "old3.md").exists()
```

#### TEST-6: test_batch_rename_preserves_order

**Beschreibung:** Prüft, dass die Reihenfolge der Umbenennungen eingehalten wird.

```python
def test_batch_rename_preserves_order(tmp_path, mocker):
    """Test that batch_rename preserves execution order"""
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()

    # Create initial file
    (test_dir / "file_a.md").write_text("content")

    persistency_manager = zt.PersistencyManager(test_dir)

    # Chained renames that depend on order:
    # file_a -> file_b -> file_c
    # This only works if order is preserved
    execution_order = []

    original_rename = persistency_manager.rename_file
    def tracking_rename(old, new):
        execution_order.append((old, new))
        original_rename(old, new)

    mocker.patch.object(persistency_manager, 'rename_file',
                        side_effect=tracking_rename)
    mocker.patch('tools4zettelkasten.cli.prompt',
                 return_value={'proceed': True})

    commands = [
        zt.cli.Rename_command('file_a.md', 'file_b.md'),
        zt.cli.Rename_command('file_b.md', 'file_c.md'),
    ]

    zt.cli.batch_rename(commands, persistency_manager)

    assert execution_order == [
        ('file_a.md', 'file_b.md'),
        ('file_b.md', 'file_c.md')
    ]
    assert (test_dir / "file_c.md").exists()
```

#### TEST-7: test_batch_rename_aborts_on_decline

**Beschreibung:** Prüft, dass bei Ablehnung keine Umbenennungen durchgeführt werden.

```python
def test_batch_rename_aborts_on_decline(tmp_path, mocker):
    """Test that batch_rename does nothing when user declines"""
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()

    (test_dir / "old.md").write_text("content")

    persistency_manager = zt.PersistencyManager(test_dir)

    commands = [
        zt.cli.Rename_command('old.md', 'new.md'),
    ]

    # Mock the prompt to return False
    mocker.patch('tools4zettelkasten.cli.prompt',
                 return_value={'proceed': False})

    zt.cli.batch_rename(commands, persistency_manager)

    # Original file should still exist
    assert (test_dir / "old.md").exists()
    assert not (test_dir / "new.md").exists()
```

#### TEST-8: test_batch_rename_empty_list

**Beschreibung:** Prüft das Verhalten bei leerer Command-Liste.

```python
def test_batch_rename_empty_list(tmp_path, mocker):
    """Test that batch_rename handles empty command list gracefully"""
    test_dir = tmp_path / "subdir"
    test_dir.mkdir()

    persistency_manager = zt.PersistencyManager(test_dir)

    # Should not prompt if list is empty
    mock_prompt = mocker.patch('tools4zettelkasten.cli.prompt')

    zt.cli.batch_rename([], persistency_manager)

    # Prompt should not have been called
    mock_prompt.assert_not_called()
```

#### TEST-9: test_format_rename_output

**Beschreibung:** Prüft die Formatierung der Ausgabe (falls als separate Funktion implementiert).

```python
def test_format_rename_output(capsys):
    """Test the formatted output of rename commands"""
    commands = [
        zt.cli.Rename_command(
            '1_5_another_Thought_2af216153.md',
            '1_2_another_Thought_2af216153.md'
        ),
    ]

    zt.cli.format_rename_output(commands)

    captured = capsys.readouterr()
    assert '1_5_another_Thought_2af216153.md' in captured.out
    assert '1_2_another_Thought_2af216153.md' in captured.out
    assert '1' in captured.out  # Nummer der Umbenennung
```

---

## Implementierungshinweise

### Dateien die geändert werden müssen

1. **`cli.py`:**
   - Neue `Rename_command`-Klasse hinzufügen
   - `batch_rename()`-Funktion refaktorieren
   - Neue Formatierungsfunktion für die Ausgabe hinzufügen

2. **`reorganize.py`:**
   - `attach_missing_ids()` anpassen
   - `attach_missing_orderings()` anpassen
   - `create_rename_commands()` anpassen
   - Import für `Rename_command` hinzufügen (bereits `cli` importiert)

3. **`tests/test_reorganize.py`:**
   - Bestehende Tests anpassen (da Rückgabetypen sich ändern)
   - Neue Tests hinzufügen

4. **`tests/test_cli.py`:** (neu)
   - Tests für `batch_rename`
   - Tests für `Rename_command`

### Reihenfolge der Implementierung

1. `Rename_command`-Klasse in `cli.py` erstellen
2. Neue Tests für `Rename_command` schreiben
3. `batch_rename()` refaktorieren
4. Tests für `batch_rename` schreiben
5. `reorganize.py` Funktionen anpassen
6. Bestehende Tests in `test_reorganize.py` anpassen
7. Alle Tests ausführen und validieren

---

## Testausführung

```bash
# Alle Tests ausführen
source venv/bin/activate && python -m pytest -v

# Nur neue Tests ausführen
source venv/bin/activate && python -m pytest -v -k "rename_command or batch_rename"

# Mit Coverage
source venv/bin/activate && python -m pytest --cov=tools4zettelkasten --cov-report=term-missing
```

## Erfolgskriterien

Die Implementierung gilt als erfolgreich, wenn:

1. Alle 41 bestehenden Tests grün sind
2. Alle neuen Tests (TEST-1 bis TEST-9) grün sind
3. Die `reorganize`-Funktion nur noch eine Bestätigung pro Batch erfordert
4. Die Ausgabe der geplanten Umbenennungen übersichtlich und verständlich ist
5. Die Reihenfolge der Umbenennungen korrekt beibehalten wird
