# Requirements: Interaktive SVG-Graph-Ansicht

## Übersicht

Die bestehende SVG-Graph-Ansicht (`/svggraph`) zeigt die Zettelkasten-Struktur als statisches SVG-Bild. Diese Ansicht soll um interaktive Funktionen erweitert werden, um eine bessere Navigation und Exploration des Zettelkastens zu ermöglichen.

## Aktueller Stand

- **Route**: `/svggraph`
- **Template**: `visualzk.html`
- **Implementierung**: `flask_views.py` generiert SVG via Graphviz
- **Graph-Erstellung**: `analyse.py` - `create_graph_of_zettelkasten()`
- **Klickbare Links**: Bereits vorhanden via `URL=fv.url_for_file(filename)` in Graphviz-Nodes
- **Problem**: SVG wird direkt in HTML eingebettet ohne Zoom/Pan-Funktionalität

## Anforderungen

### REQ-1: Zoom-Funktionalität

Das SVG soll zoombar sein:
- **REQ-1.1**: Pinch-to-Zoom auf Touch-Geräten (Zwei-Finger-Geste)
- **REQ-1.2**: Mausrad-Zoom auf Desktop-Geräten
- **REQ-1.3**: Zoom-Buttons (+/-) als Alternative, die nach Scrollen sichtbar bleiben (fixed position)
- **REQ-1.4**: Zoom-Bereich sinnvoll begrenzen (z.B. 10% bis 500%)

### REQ-2: Pan-Funktionalität (Verschieben)

Das SVG soll verschiebbar sein:
- **REQ-2.1**: Drag-to-Pan mit Maus (Klicken und Ziehen)
- **REQ-2.2**: Touch-Pan auf Touch-Geräten (Ein-Finger-Geste)
- **REQ-2.3**: Cursor ändert sich zu "grab"/"grabbing" während Pan

### REQ-3: Klickbare Notizen

Die Notiz-Knoten im Graph sollen zur entsprechenden Notiz navigieren:
- **REQ-3.1**: Klick auf Knoten öffnet die Notiz-Detailansicht (`/filename`)
- **REQ-3.2**: Bereits implementiert via Graphviz `URL`-Attribut - muss erhalten bleiben
- **REQ-3.3**: Hover-Effekt zur Visualisierung der Klickbarkeit

### REQ-4: Rücksprung zur Graph-Ansicht

Nach dem Betrachten einer Notiz soll der Benutzer zur Graph-Ansicht zurückkehren können:
- **REQ-4.1**: Browser-Back-Button funktioniert (Standard-Verhalten)
- **REQ-4.2**: Zoom- und Pan-Position werden beim Rücksprung wiederhergestellt
- **REQ-4.3**: Optional: Expliziter "Zurück zum Graph"-Link in der Notiz-Ansicht

### REQ-5: Benutzerfreundlichkeit

- **REQ-5.1**: Initiale Ansicht zeigt den gesamten Graph (fit-to-view)
- **REQ-5.2**: Reset-Button um zur initialen Ansicht zurückzukehren
- **REQ-5.3**: Visuelle Hinweise für Zoom-Level (z.B. Prozentanzeige)

## Technische Umsetzung

### Empfohlene Bibliothek: SVG.js mit svg-pan-zoom Plugin

**Alternative 1: svg-pan-zoom (leichtgewichtig)**
- Standalone-Bibliothek, keine Abhängigkeiten
- CDN: `https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js`
- Unterstützt Touch-Gesten, Mausrad, programmatische Kontrolle

**Alternative 2: panzoom**
- Noch leichtgewichtiger
- CDN: `https://cdn.jsdelivr.net/npm/panzoom@9.4.3/dist/panzoom.min.js`

### Zu ändernde Dateien

1. **`flask_frontend/templates/visualzk.html`**
   - SVG in Container-Element wrappen
   - JavaScript für Pan/Zoom einbinden
   - Zoom-Buttons hinzufügen (fixed position)
   - CSS für Hover-Effekte

2. **`flask_frontend/templates/mainpage.html`** (optional)
   - "Zurück zum Graph"-Link hinzufügen

3. **`flask_views.py`**
   - Keine Änderungen erforderlich (SVG-Generierung bleibt gleich)

### Zustandserhaltung bei Rücksprung

Für REQ-4.2 (Zoom/Pan-Position erhalten) gibt es zwei Optionen:

**Option A: Browser History API**
- Zoom/Pan-Zustand in URL-Hash speichern (z.B. `#zoom=1.5&x=100&y=200`)
- Bei Rückkehr aus Hash wiederherstellen

**Option B: sessionStorage**
- Zoom/Pan-Zustand vor Navigation speichern
- Bei Laden der Seite wiederherstellen

## Testspezifikationen

### TEST-1: Zoom mit Mausrad
- Mausrad nach oben → Zoom In
- Mausrad nach unten → Zoom Out
- Zoom-Grenzen werden eingehalten

### TEST-2: Zoom mit Buttons
- Klick auf "+" → Zoom In
- Klick auf "-" → Zoom Out
- Buttons bleiben bei Scrollen sichtbar

### TEST-3: Pinch-to-Zoom (Touch)
- Zwei-Finger-Spreizen → Zoom In
- Zwei-Finger-Zusammenziehen → Zoom Out

### TEST-4: Pan mit Maus
- Klicken und Ziehen verschiebt den Graph
- Cursor ändert sich während Drag

### TEST-5: Pan mit Touch
- Ein-Finger-Ziehen verschiebt den Graph

### TEST-6: Notiz-Navigation
- Klick auf Knoten öffnet Notiz
- Browser-Back kehrt zum Graph zurück
- Zoom/Pan-Position ist wiederhergestellt

### TEST-7: Reset-Funktion
- Reset-Button stellt initiale Ansicht wieder her

### TEST-8: Hover-Effekt
- Hover über Knoten zeigt visuelles Feedback

## Akzeptanzkriterien

- [ ] Alle Tests (TEST-1 bis TEST-8) bestanden
- [ ] Funktioniert auf Desktop (Chrome, Firefox, Safari)
- [ ] Funktioniert auf mobilen Geräten (iOS Safari, Android Chrome)
- [ ] Keine Regression: Bestehende Klickbarkeit der Knoten funktioniert weiterhin
- [ ] Performance: Zoom/Pan flüssig auch bei großen Graphen (100+ Knoten)
- [ ] Gesamte Testsuite (`pytest`) läuft erfolgreich durch
- [ ] Keine bestehende Funktionalität wird verändert (Regressionstest)
- [ ] Dokumentation (README.rst, docs_source/) ggf. angepasst
