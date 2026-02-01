# Requirements: Hierarchische Sortierung der Listenansicht

## Übersicht

Die Listenansicht (`/` Route) sortiert Dateien derzeit alphabetisch, was zu einer falschen Reihenfolge führt. Eltern-Notizen sollten vor ihren Kind-Notizen erscheinen, was bei alphabetischer Sortierung nicht garantiert ist.

## Aktueller Stand

- **Route**: `/` in `flask_views.py`
- **Aktuelle Sortierung**: `zettelkasten_list.sort()` (alphabetisch)
- **Problem**: `12_01_01` erscheint vor `12_01`, obwohl `12_01` hierarchisch übergeordnet ist

### Beispiel des Problems

| Alphabetische Sortierung (falsch) | Erwartete hierarchische Sortierung |
|-----------------------------------|-----------------------------------|
| `12_01_01_Topic_A_abc.md` | `12_Topic_C_ghi.md` |
| `12_01_Topic_B_def.md` | `12_01_Topic_B_def.md` |
| `12_Topic_C_ghi.md` | `12_01_01_Topic_A_abc.md` |

### Warum funktioniert es in der Graph-Ansicht?

Die Graph-Ansicht nutzt bereits die existierenden Funktionen in `reorganize.py`:
- `generate_tokenized_list()` - Zerlegt Dateinamen in Ordering-Token
- `generate_tree()` - Baut hierarchischen Baum auf
- `get_hierarchy_links()` - Extrahiert Struktur-Links

Diese Logik berücksichtigt die hierarchische Struktur korrekt.

## Anforderungen

### REQ-1: Hierarchische Sortierung

Die Listenansicht soll Dateien hierarchisch sortieren:
- **REQ-1.1**: Eltern-Notizen erscheinen vor ihren Kind-Notizen
- **REQ-1.2**: Geschwister-Notizen werden numerisch sortiert
- **REQ-1.3**: Alphanumerische Orderings (z.B. `12_01a`) werden korrekt behandelt

### REQ-2: Konsistenz mit Graph-Ansicht

- **REQ-2.1**: Die Sortierreihenfolge entspricht der Struktur im Graph
- **REQ-2.2**: Wiederverwendung der existierenden Baum-Logik aus `reorganize.py`

### REQ-3: Keine Regression

- **REQ-3.1**: Bestehende Funktionalität bleibt erhalten
- **REQ-3.2**: Alle existierenden Tests laufen weiterhin erfolgreich

## Technische Umsetzung

### Ansatz: Baum-basierte Sortierung (Option 2)

Die existierende `generate_tree()` Funktion wird genutzt und der Baum in eine flache, korrekt sortierte Liste umgewandelt.

### Neue Funktion: `flatten_tree_to_list()`

```python
def flatten_tree_to_list(tree: list) -> list[str]:
    """Wandelt einen hierarchischen Baum in eine flache, sortierte Liste um.

    Der Baum hat die Form:
    [['1', 'filename1.md', [['1', 'filename1_1.md'], ['2', 'filename1_2.md']]],
     ['2', 'filename2.md']]

    Die Ausgabe ist eine flache Liste in hierarchischer Reihenfolge:
    ['filename1.md', 'filename1_1.md', 'filename1_2.md', 'filename2.md']
    """
```

### Zu ändernde Dateien

1. **`reorganize.py`**
   - Neue Funktion `flatten_tree_to_list()` hinzufügen

2. **`flask_views.py`**
   - `index()` Funktion anpassen:
     - `generate_tokenized_list()` und `generate_tree()` aufrufen
     - `flatten_tree_to_list()` für sortierte Liste nutzen

### Algorithmus für `flatten_tree_to_list()`

```
FUNKTION flatten_tree_to_list(tree):
    result = []
    FÜR JEDEN knoten IN tree:
        WENN knoten Dateiname hat:
            result.append(dateiname)
        WENN knoten Kinder hat:
            result.extend(flatten_tree_to_list(kinder))
    RETURN result
```

### Codeänderung in `flask_views.py`

```python
# Vorher:
zettelkasten_list = persistencyManager.get_list_of_filenames()
zettelkasten_list.sort()

# Nachher:
zettelkasten_list = persistencyManager.get_list_of_filenames()
tokenized_list = ro.generate_tokenized_list(zettelkasten_list)
tree = ro.generate_tree(tokenized_list)
zettelkasten_list = ro.flatten_tree_to_list(tree)
```

## Testspezifikationen

### TEST-1: Eltern vor Kindern

```python
def test_flatten_tree_parent_before_children():
    """Eltern-Notizen erscheinen vor Kind-Notizen."""
    filenames = [
        '12_01_01_Child_abc.md',
        '12_01_Parent_def.md',
        '12_Grandparent_ghi.md'
    ]
    sorted_list = hierarchical_sort(filenames)
    assert sorted_list.index('12_Grandparent_ghi.md') < sorted_list.index('12_01_Parent_def.md')
    assert sorted_list.index('12_01_Parent_def.md') < sorted_list.index('12_01_01_Child_abc.md')
```

### TEST-2: Geschwister numerisch sortiert

```python
def test_flatten_tree_siblings_sorted():
    """Geschwister-Notizen werden numerisch sortiert."""
    filenames = [
        '1_10_Topic_abc.md',
        '1_2_Topic_def.md',
        '1_1_Topic_ghi.md'
    ]
    sorted_list = hierarchical_sort(filenames)
    assert sorted_list == [
        '1_1_Topic_ghi.md',
        '1_2_Topic_def.md',
        '1_10_Topic_abc.md'
    ]
```

### TEST-3: Alphanumerische Orderings

```python
def test_flatten_tree_alphanumeric_ordering():
    """Alphanumerische Orderings werden korrekt behandelt."""
    filenames = [
        '1_2_Topic_abc.md',
        '1_1a_Topic_def.md',
        '1_1_Topic_ghi.md'
    ]
    sorted_list = hierarchical_sort(filenames)
    assert sorted_list.index('1_1_Topic_ghi.md') < sorted_list.index('1_1a_Topic_def.md')
    assert sorted_list.index('1_1a_Topic_def.md') < sorted_list.index('1_2_Topic_abc.md')
```

### TEST-4: Leere Liste

```python
def test_flatten_tree_empty_list():
    """Leere Listen werden korrekt behandelt."""
    sorted_list = hierarchical_sort([])
    assert sorted_list == []
```

### TEST-5: Einzelne Datei

```python
def test_flatten_tree_single_file():
    """Einzelne Dateien werden korrekt behandelt."""
    filenames = ['1_Topic_abc.md']
    sorted_list = hierarchical_sort(filenames)
    assert sorted_list == ['1_Topic_abc.md']
```

### TEST-6: Konsistenz mit Graph

```python
def test_list_order_matches_graph_structure():
    """Listenreihenfolge entspricht der Graph-Struktur."""
    # Vergleiche Reihenfolge aus flatten_tree mit structure_links
```

### TEST-7: Flask-Route liefert korrekte Reihenfolge

```python
def test_index_returns_hierarchically_sorted_list(client):
    """Die Index-Route liefert hierarchisch sortierte Liste."""
    response = client.get('/')
    # Prüfe Reihenfolge im HTML
```

## Akzeptanzkriterien

- [ ] Alle Tests (TEST-1 bis TEST-7) bestanden
- [ ] Eltern-Notizen erscheinen immer vor ihren Kind-Notizen
- [ ] Alphanumerische Orderings werden korrekt sortiert
- [ ] Gesamte Testsuite (`pytest`) läuft erfolgreich durch
- [ ] Keine bestehende Funktionalität wird verändert (Regressionstest)
- [ ] Dokumentation (README.rst, docs_source/) ggf. angepasst

## Abhängigkeiten

- Nutzt existierende Funktionen aus `reorganize.py`:
  - `generate_tokenized_list()`
  - `generate_tree()`
- Import von `reorganize` in `flask_views.py` (ggf. hinzufügen)
