# UnrealGitUI

Kompakte Desktop-Anwendung zur Unterstützung von Git-Workflows in Unreal-Projekten. Dieses Repository bietet eine kleine UI, GitHub-Integrationen und Konfigurationswerkzeuge, die speziell auf die Bedürfnisse von Unreal-Entwickler*innen zugeschnitten sind.

## Inhalt
- Startpunkt: `run.py`
- Hauptanwendung: `main/main.py`
- Konfiguration: `main/config.py`, `main/config.json`
- UI-Tabs: `ui/tabs/dashboard.py`, `ui/tabs/terminal.py`, `ui/tabs/unreal_tools.py`
- GitHub-Tools: `main/github_tools/dashboard.py`, `main/github_tools/token.py`
- Externe Widgets: `main/ctk_external_modules/CTkCollapsibleFrame.py`
- Tests: `tests/test_config.py`

## Features
- Lokale UI für gängige Git-Aufgaben (Branching, Commit, Status)
- Integration mit GitHub (Token-Management, Dashboard-Übersicht)
- Konfigurierbar per JSON
- Erweiterbare CTk-basierte Widgets

## Voraussetzungen
- Python 3.8 oder neuer
- Empfohlen: virtuelle Umgebung

## Installation
1. Repository klonen:

```bash
git clone <repo-url>
cd UnrealGitUI
```

2. Virtuelle Umgebung erstellen und aktivieren:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

3. Abhängigkeiten installieren (sofern erforderlich):

```bash
pip install -e .
```

## Schnellstart
Die Anwendung lokal starten:

```bash
python run.py
```

Konfiguration über `main/config.json` oder die Lader/Parser in `main/config.py`.

## Tests
Unit-Tests mit `pytest` ausführen:

```bash
pytest
# gezielter Test
pytest tests/test_config.py
```

## Entwicklung
- UI-Änderungen in `ui/` vornehmen
- GitHub-Logik in `main/github_tools/` pflegen
- Neue Widgets in `main/ctk_external_modules/` ergänzen
- Tests in `tests/` hinzufügen oder erweitern

## Sicherheit
- Tokens sicher aufbewahren und nie in Repositories committen. Verwende die Token-Hilfen in `main/github_tools/token.py`.

## Mitwirken
- Issues und Pull Requests sind willkommen – bitte beschreibe Änderungen kurz und liefere Tests für neue Logik.

---

Bei Fragen oder wenn du Hilfe beim Einrichten brauchst, öffne ein Issue oder kontaktiere die Maintainer.
