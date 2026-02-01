# Requirements: Navigation zwischen Notizen (Vorherige/Nächste)

## Übersicht

Die Detailansicht einer Notiz soll um Navigation zur vorherigen und nächsten Notiz erweitert werden. Die Reihenfolge basiert auf der hierarchischen Sortierung (Eltern vor Kindern), nicht auf alphabetischer Sortierung.

## Aktueller Stand

- **Route**: `/<file>` in `flask_views.py`
- **Template**: `mainpage.html`
- **Aktuelle Navigation**: Nur "edit" und "List of Notes" Links
- **Sortierung**: Hierarchische Sortierung via `flatten_tree_to_list()` bereits implementiert

### Aktuelle UI (mainpage.html, Zeile 35-36)

```html
<a href="{{ url_for('edit', filename = filename) }}"> edit </a> <br>
<a href="{{ url_for('index') }}"> List of Notes </a>
```

## Anforderungen

### REQ-1: Visuelle Navigation (Bootstrap-Buttons)

- **REQ-1.1**: Button-Gruppe am Fuß der Notiz mit vier Aktionen:
  - Vorherige Notiz (◀)
  - Zur Liste (📋)
  - Bearbeiten (✏️)
  - Nächste Notiz (▶)
- **REQ-1.2**: Buttons sind touch-freundlich (ausreichend groß)
- **REQ-1.3**: Konsistentes Design mit Bootstrap 5
- **REQ-1.4**: Responsive Layout (funktioniert auf Desktop und Mobil)

### REQ-2: Hierarchische Reihenfolge

- **REQ-2.1**: Vorherige/Nächste basiert auf `flatten_tree_to_list()` Sortierung
- **REQ-2.2**: Eltern-Notizen kommen vor Kind-Notizen
- **REQ-2.3**: Geschwister-Notizen sind in korrekter Reihenfolge

### REQ-3: Randfall-Behandlung

- **REQ-3.1**: Erste Notiz: "Vorherige"-Button ist deaktiviert (disabled)
- **REQ-3.2**: Letzte Notiz: "Nächste"-Button ist deaktiviert (disabled)
- **REQ-3.3**: Deaktivierte Buttons sind visuell erkennbar (ausgegraut)

### REQ-4: Tastatur-Navigation

- **REQ-4.1**: `←` (Pfeil links) = Vorherige Notiz
- **REQ-4.2**: `→` (Pfeil rechts) = Nächste Notiz
- **REQ-4.3**: `l` = Zur Liste
- **REQ-4.4**: `e` = Bearbeiten
- **REQ-4.5**: Tastatur-Shortcuts funktionieren nur wenn kein Eingabefeld fokussiert ist

### REQ-5: Keine Regression

- **REQ-5.1**: Bestehende Funktionalität bleibt erhalten
- **REQ-5.2**: Alle existierenden Tests laufen erfolgreich

## UI-Design

### Wireframe: Button-Gruppe am Fuß

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                      [Notiz-Inhalt]                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │◀ Vorherige│  │ 📋 Liste │  │ ✏️ Edit  │  │ Nächste ▶│   │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Beispiel: Deaktivierter Button (erste Notiz)

```
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │◀ Vorherige│  │ 📋 Liste │  │ ✏️ Edit  │  │ Nächste ▶│
   └──────────┘  └──────────┘  └──────────┘  └──────────┘
    (disabled)      (aktiv)      (aktiv)       (aktiv)
```

### Tastatur-Hinweis (optional)

Kleiner Hinweistext unter den Buttons:
```
Tastatur: ← Vorherige | → Nächste | L Liste | E Edit
```

## Technische Umsetzung

### Änderungen in `flask_views.py`

Die `show_md_file()` Funktion muss erweitert werden:

```python
@app.route('/<file>')
def show_md_file(file):
    persistencyManager = PersistencyManager(st.ZETTELKASTEN)

    # Hierarchisch sortierte Liste ermitteln
    zettelkasten_list = persistencyManager.get_list_of_filenames()
    tokenized_list = ro.generate_tokenized_list(zettelkasten_list)
    tree = ro.generate_tree(tokenized_list)
    sorted_list = ro.flatten_tree_to_list(tree)

    # Position der aktuellen Datei ermitteln
    current_index = sorted_list.index(file)

    # Vorherige und nächste Datei ermitteln
    previous_file = sorted_list[current_index - 1] if current_index > 0 else None
    next_file = sorted_list[current_index + 1] if current_index < len(sorted_list) - 1 else None

    # ... bestehender Code ...

    return render_template(
        "mainpage.html",
        codeCSSString="<style>" + css_string + "</style>",
        htmlString=htmlString,
        filename=filename,
        previous_file=previous_file,  # NEU
        next_file=next_file           # NEU
    )
```

### Neue Hilfsfunktion (optional)

```python
def get_adjacent_files(filename: str, sorted_list: list) -> tuple:
    """Ermittelt vorherige und nächste Datei in der hierarchischen Liste.

    :param filename: Aktuelle Datei
    :param sorted_list: Hierarchisch sortierte Dateiliste
    :return: Tuple (previous_file, next_file), None wenn nicht vorhanden
    """
    try:
        current_index = sorted_list.index(filename)
    except ValueError:
        return (None, None)

    previous_file = sorted_list[current_index - 1] if current_index > 0 else None
    next_file = sorted_list[current_index + 1] if current_index < len(sorted_list) - 1 else None

    return (previous_file, next_file)
```

### Änderungen in `mainpage.html`

```html
<!-- Navigation am Fuß der Notiz -->
<nav class="navbar fixed-bottom navbar-light bg-light">
  <div class="container-fluid justify-content-center">
    <div class="btn-group" role="group" aria-label="Notiz-Navigation">
      {% if previous_file %}
        <a href="{{ url_for('show_md_file', file=previous_file) }}" class="btn btn-outline-primary">
          ◀ Vorherige
        </a>
      {% else %}
        <button class="btn btn-outline-secondary" disabled>◀ Vorherige</button>
      {% endif %}

      <a href="{{ url_for('index') }}" class="btn btn-outline-primary">📋 Liste</a>
      <a href="{{ url_for('edit', filename=filename) }}" class="btn btn-outline-primary">✏️ Edit</a>

      {% if next_file %}
        <a href="{{ url_for('show_md_file', file=next_file) }}" class="btn btn-outline-primary">
          Nächste ▶
        </a>
      {% else %}
        <button class="btn btn-outline-secondary" disabled>Nächste ▶</button>
      {% endif %}
    </div>
  </div>
</nav>

<!-- JavaScript für Tastatur-Navigation -->
<script>
document.addEventListener('keydown', function(e) {
  // Nicht reagieren wenn in Eingabefeld
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

  switch(e.key) {
    case 'ArrowLeft':
      {% if previous_file %}
        window.location.href = "{{ url_for('show_md_file', file=previous_file) }}";
      {% endif %}
      break;
    case 'ArrowRight':
      {% if next_file %}
        window.location.href = "{{ url_for('show_md_file', file=next_file) }}";
      {% endif %}
      break;
    case 'l':
    case 'L':
      window.location.href = "{{ url_for('index') }}";
      break;
    case 'e':
    case 'E':
      window.location.href = "{{ url_for('edit', filename=filename) }}";
      break;
  }
});
</script>
```

## Testspezifikationen

### TEST-1: Vorherige/Nächste werden korrekt ermittelt

```python
def test_get_adjacent_files_middle():
    """Mittlere Datei hat Vorherige und Nächste."""
    sorted_list = ['a.md', 'b.md', 'c.md']
    prev, next = get_adjacent_files('b.md', sorted_list)
    assert prev == 'a.md'
    assert next == 'c.md'
```

### TEST-2: Erste Datei hat keine Vorherige

```python
def test_get_adjacent_files_first():
    """Erste Datei hat keine Vorherige."""
    sorted_list = ['a.md', 'b.md', 'c.md']
    prev, next = get_adjacent_files('a.md', sorted_list)
    assert prev is None
    assert next == 'b.md'
```

### TEST-3: Letzte Datei hat keine Nächste

```python
def test_get_adjacent_files_last():
    """Letzte Datei hat keine Nächste."""
    sorted_list = ['a.md', 'b.md', 'c.md']
    prev, next = get_adjacent_files('c.md', sorted_list)
    assert prev == 'b.md'
    assert next is None
```

### TEST-4: Einzelne Datei

```python
def test_get_adjacent_files_single():
    """Einzelne Datei hat weder Vorherige noch Nächste."""
    sorted_list = ['a.md']
    prev, next = get_adjacent_files('a.md', sorted_list)
    assert prev is None
    assert next is None
```

### TEST-5: Datei nicht in Liste

```python
def test_get_adjacent_files_not_found():
    """Nicht existierende Datei gibt None zurück."""
    sorted_list = ['a.md', 'b.md']
    prev, next = get_adjacent_files('x.md', sorted_list)
    assert prev is None
    assert next is None
```

### TEST-6: Hierarchische Reihenfolge

```python
def test_navigation_uses_hierarchical_order():
    """Navigation verwendet hierarchische, nicht alphabetische Reihenfolge."""
    # 12.md ist Eltern von 12_01.md
    filenames = ['12_01_Child_abc.md', '12_Parent_def.md']
    tokenized = generate_tokenized_list(filenames)
    tree = generate_tree(tokenized)
    sorted_list = flatten_tree_to_list(tree)

    # Hierarchisch: Parent vor Child
    assert sorted_list.index('12_Parent_def.md') < sorted_list.index('12_01_Child_abc.md')

    prev, next = get_adjacent_files('12_01_Child_abc.md', sorted_list)
    assert prev == '12_Parent_def.md'
```

### TEST-7: Flask-Route enthält Navigation

```python
def test_show_md_file_includes_navigation(client):
    """Die Notiz-Ansicht enthält Navigations-Buttons."""
    response = client.get('/some_note.md')
    html = response.data.decode('utf-8')
    assert 'Vorherige' in html or 'previous' in html.lower()
    assert 'Nächste' in html or 'next' in html.lower()
```

### TEST-8: Deaktivierte Buttons

```python
def test_first_note_has_disabled_previous(client):
    """Erste Notiz hat deaktivierten Vorherige-Button."""
    # Test mit erster Notiz in hierarchischer Reihenfolge
    response = client.get('/first_note.md')
    html = response.data.decode('utf-8')
    assert 'disabled' in html
```

## Akzeptanzkriterien

- [ ] Alle Tests (TEST-1 bis TEST-8) bestanden
- [ ] Neue Tests in Testsuite aufgenommen (`test_flask_views.py`) für spätere Regressionen
- [ ] Visuelle Navigation mit Bootstrap-Buttons funktioniert
- [ ] Tastatur-Navigation (←, →, L, E) funktioniert
- [ ] Hierarchische Reihenfolge wird verwendet (Eltern vor Kindern)
- [ ] Erste/Letzte Notiz: Entsprechende Buttons sind deaktiviert
- [ ] Responsive Design (Desktop und Mobil)
- [ ] Gesamte Testsuite (`pytest`) läuft erfolgreich durch
- [ ] Keine bestehende Funktionalität wird verändert (Regressionstest)
- [ ] Dokumentation (README.rst, docs_source/) ggf. angepasst

## Abhängigkeiten

- Nutzt existierende Funktionen aus `reorganize.py`:
  - `generate_tokenized_list()`
  - `generate_tree()`
  - `flatten_tree_to_list()`
- Bootstrap 5 (bereits eingebunden)

## Zu ändernde Dateien

| Datei | Änderung |
|-------|----------|
| `flask_views.py` | `show_md_file()` erweitern, ggf. Hilfsfunktion hinzufügen |
| `mainpage.html` | Navigation-Buttons und JavaScript für Tastatur |
| `test_flask_views.py` | Neue Tests für Navigation |
