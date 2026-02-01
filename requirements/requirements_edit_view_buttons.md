# Requirements: Verbesserung der Edit-Ansicht (Save/Cancel Buttons)

## Übersicht

Die Edit-Ansicht einer Notiz soll verbessert werden. Der "Submit"-Button soll in "Save" umbenannt werden und ein "Cancel"-Button zum Verlassen ohne Speichern hinzugefügt werden. Das Design soll konsistent mit den Navigations-Buttons der Notiz-Detailansicht sein.

## Aktueller Stand

- **Route**: `/edit/<filename>` in `flask_views.py`
- **Template**: `edit.html`
- **Form-Klasse**: `PageDownForm` mit `SubmitField('Submit')`

### Aktuelle UI (edit.html)

```html
<form method="POST">
  {{ form.hidden_tag() }}
  {{ form.pagedown(rows=10, style='width:100%') }}
  {{ form.submit }}
</form>
```

**Probleme:**
1. Button-Text ist "Submit" statt "Save"
2. Keine Möglichkeit, den Edit-Modus ohne Speichern zu verlassen
3. Button-Styling inkonsistent mit der neuen Navigations-UI

## Anforderungen

### REQ-1: Button-Umbenennung

- **REQ-1.1**: "Submit" wird zu "Save" umbenannt
- **REQ-1.2**: Button-Text ist klar und verständlich

### REQ-2: Cancel-Button hinzufügen

- **REQ-2.1**: "Cancel"-Button führt zurück zur Notiz-Ansicht ohne zu speichern
- **REQ-2.2**: Cancel-Button ist visuell als sekundäre Aktion erkennbar (anderer Stil als Save)
- **REQ-2.3**: Bei ungespeicherten Änderungen: Optional eine Bestätigungsabfrage (nice-to-have)

### REQ-3: Konsistentes Button-Design

- **REQ-3.1**: Buttons verwenden Bootstrap 5 Styling wie in `mainpage.html`
- **REQ-3.2**: Button-Gruppe ähnlich der Navigations-Footer-Leiste
- **REQ-3.3**: Responsive Design für mobile Geräte

### REQ-4: Fixed Footer für Buttons

- **REQ-4.1**: Buttons in fixierter Footer-Leiste (wie bei Notiz-Detailansicht)
- **REQ-4.2**: Buttons sind immer sichtbar, auch bei langen Notizen

### REQ-5: Keine Regression

- **REQ-5.1**: Bestehende Speicher-Funktionalität bleibt erhalten
- **REQ-5.2**: Alle existierenden Tests laufen erfolgreich
- **REQ-5.3**: Neue Tests werden zur Testsuite hinzugefügt für spätere Regressionen

## UI-Design

### Wireframe: Button-Gruppe am Fuß

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                   [Markdown Editor]                         │
│                                                             │
│                   [Live Preview]                            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│          ┌──────────────┐      ┌──────────────┐            │
│          │   Cancel     │      │     Save     │            │
│          └──────────────┘      └──────────────┘            │
│           (secondary)            (primary)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Button-Styling

| Button | Bootstrap-Klasse | Aktion |
|--------|------------------|--------|
| Cancel | `btn btn-outline-secondary` | Zurück zur Notiz ohne Speichern |
| Save | `btn btn-primary` | Speichern und zurück zur Notiz |

## Technische Umsetzung

### Änderungen in `flask_views.py`

1. **PageDownForm anpassen:**
```python
class PageDownForm(FlaskForm):
    pagedown = PageDownField('Enter your markdown')
    submit = SubmitField('Save')  # Umbenannt von 'Submit'
```

2. **edit() Funktion erweitern:**
```python
@app.route('/edit/<filename>', methods=['GET', 'POST'])
def edit(filename):
    # ... bestehender Code ...
    return render_template('edit.html', form=form, filename=filename)  # filename hinzufügen
```

### Änderungen in `edit.html`

```html
<!-- Platz für fixierte Footer-Leiste -->
<style>
  body {
    padding-bottom: 80px;
  }
  .edit-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #f8f9fa;
    border-top: 1px solid #dee2e6;
    padding: 10px 0;
    z-index: 1000;
  }
  .edit-footer .btn-group {
    display: flex;
    justify-content: center;
    gap: 10px;
  }
  .edit-footer .btn {
    min-width: 120px;
  }
</style>

<!-- Form ohne Submit-Button im Body -->
<form method="POST" id="edit-form">
  {{ form.hidden_tag() }}
  {{ form.pagedown(rows=10, style='width:100%') }}
</form>

<!-- Fixierte Footer-Leiste -->
<footer class="edit-footer">
  <div class="container">
    <div class="btn-group">
      <a href="{{ url_for('show_md_file', file=filename) }}" class="btn btn-outline-secondary">
        Cancel
      </a>
      <button type="submit" form="edit-form" class="btn btn-primary">
        Save
      </button>
    </div>
  </div>
</footer>
```

## Testspezifikationen

### TEST-1: Save-Button vorhanden

```python
def test_edit_view_has_save_button(client):
    """Edit-Ansicht hat Save-Button."""
    response = client.get('/edit/some_note.md')
    html = response.data.decode('utf-8')
    assert 'Save' in html
```

### TEST-2: Cancel-Button vorhanden

```python
def test_edit_view_has_cancel_button(client):
    """Edit-Ansicht hat Cancel-Button."""
    response = client.get('/edit/some_note.md')
    html = response.data.decode('utf-8')
    assert 'Cancel' in html
```

### TEST-3: Cancel-Link führt zur Notiz

```python
def test_cancel_links_to_note_view(client):
    """Cancel-Button führt zur Notiz-Ansicht."""
    response = client.get('/edit/some_note.md')
    html = response.data.decode('utf-8')
    assert 'show_md_file' in html or '/some_note.md' in html
```

### TEST-4: Speichern funktioniert weiterhin

```python
def test_save_still_works(client, tmp_path):
    """Speichern-Funktionalität ist nicht beschädigt."""
    # Test dass POST-Request Datei speichert
```

### TEST-5: Kein Submit-Text mehr

```python
def test_no_submit_text(client):
    """'Submit'-Text ist nicht mehr vorhanden."""
    response = client.get('/edit/some_note.md')
    html = response.data.decode('utf-8')
    # Submit sollte nicht als Button-Text erscheinen
    assert '>Submit<' not in html
```

## Akzeptanzkriterien

- [ ] Alle Tests (TEST-1 bis TEST-5) bestanden
- [ ] Neue Tests in Testsuite aufgenommen (`test_flask_views.py`) für spätere Regressionen
- [ ] "Save"-Button speichert und kehrt zur Notiz zurück
- [ ] "Cancel"-Button kehrt zur Notiz zurück ohne zu speichern
- [ ] Button-Design konsistent mit Navigations-Buttons in `mainpage.html`
- [ ] Fixed Footer für Buttons
- [ ] Responsive Design (Desktop und Mobil)
- [ ] Gesamte Testsuite (`pytest`) läuft erfolgreich durch
- [ ] Keine bestehende Funktionalität wird verändert (Regressionstest)
- [ ] Dokumentation (README.rst, docs_source/) ggf. angepasst

## Zu ändernde Dateien

| Datei | Änderung |
|-------|----------|
| `flask_views.py` | `PageDownForm` Submit-Label ändern, `filename` an Template übergeben |
| `edit.html` | Neues Layout mit Fixed Footer und Bootstrap-Buttons |
| `test_flask_views.py` | Neue Tests für Edit-View Buttons |
