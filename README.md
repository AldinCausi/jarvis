# Jarvis – Sprachassistent mit Python

Es handelt sich um einen Sprachassistenten für das Terminal. Man hält eine Taste gedrückt spricht etwas ein und bekommt eine Antowrt eines OpenAI Modells vorgelesen. Dabei wird auch Function Calling verwendet.

## Funktionen

- **Push-to-talk:** Die Aufnahme läuft, solange die Taste `A` gehalten wird.
- **Lokale Spracherkennung:** Die Aufnahme wird mit `faster-whisper` (Modell `base`, Sprache Deutsch) auf dem eigenen Rechner transkribiert.
- **Antworten per Sprachmodell:** Der Text geht an ein OpenAI-Modell, die Antwort wird per Text-to-Speech ausgegeben.
- **Function Calling:** Das Modell entscheidet selbst, ob und welche Tools es aufruft, befüllt deren Parameter und kann mehrere Tools pro Anfrage nutzen. Die Ergebnisse fließen in die Antwort ein.
- **Dauerdialog:** Das Gespräch läuft weiter, bis der Nutzer zu verstehen gibt, dass er fertig ist. Dann beendet das Modell das Programm über ein Tool.
- **Gedächtnis:** Der Gesprächsverlauf wird in SQLite gespeichert und beim nächsten Start wieder geladen.

### Verfügbare Tools

| Tool | Beschreibung |
| --- | --- |
| `get_current_time` | Gibt die aktuelle Uhrzeit zurück |
| `create_note` | Legt eine Textdatei in `~/Schreibtisch/Notizen` an |
| `delete_note` | Löscht eine Notiz aus diesem Ordner |
| `stop_program` | Beendet den Assistenten |

## Technologien

Python3, faster-whisper, OpenAI API (Responses API, Function Calling, Text-to-Speech), SQLite, sounddevice, soundfile, evdev, python-dotenv

## Projektstruktur

```
main.py          Aufnahme, Transkription, Modellanfrage, Tool-Schleife, Sprachausgabe
tools.py         Tool-Funktionen und deren Schemas (TOOLS, FUNCTIONS)
database.py      Speicherung und Laden des Gesprächsverlaufs (SQLite)
requirements.txt Abhängigkeiten
```

## Voraussetzungen

- Linux (die Tastatursteuerung nutzt `evdev`)
- Python 3.13 (laut `requirements.txt` werden Pakete für Python 3.13 verwendet)
- Ein OpenAI-API-Schlüssel
- Mikrofon und Lautsprecher

## Installation

```bash
git clone https://github.com/AldinCausi/jarvis.git
cd jarvis
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Beim ersten Start wird das Whisper-Modell automatisch heruntergeladen.

## Konfiguration

1. **API-Schlüssel:** Lege eine Datei `.env` im Projektordner an:

   ```
   OPENAI_API_KEY=dein_schluessel
   ```

2. **Tastatur-Gerät:** In `main.py` ist das Eingabegerät fest eingetragen (`/dev/input/event3`). Das richtige Gerät findest du mit:

   ```bash
   python3 -m evdev.evtest
   ```

   Passe den Pfad in `main.py` an. Damit das Programm Tastaturereignisse lesen darf, muss dein Benutzer in der Gruppe `input` sein oder das Programm mit entsprechenden Rechten laufen.

3. **Notizen-Ordner:** Lege `~/Schreibtisch/Notizen` an (bei englischer Systemsprache den Pfad in `tools.py` anpassen).

## Benutzung

```bash
python3 main.py
```

1. Taste `A` gedrückt halten und sprechen.
2. Taste loslassen. Modell transkribiert, antwortet und liest die Antwort vor.
3. Wiederholen. Mit einer Aussage wie „Danke, das war alles“ beendet sich Jarvis.

Beispiele: „Wie spät ist es?“, „Erstelle eine Notiz mit meiner Einkaufsliste“, „Lösche die Notiz Einkaufsliste“.

## Bekannte Einschränkungen

- Nur unter Linux lauffähig, Tastaturgerät und Notizen-Pfad sind fest eingetragen.
- Die Taste `A` wird systemweit mitgelesen, auch wenn ein anderes Fenster aktiv ist.
- Der Gesprächsverlauf wächst unbegrenzt und wird komplett an das Modell gesendet.

## Mögliche Erweiterungen

- Konfigurierbare Pfade und Tasten über die `.env`
- Fehlerbehandlung in den Notiz-Tools
- Weitere Tools, zum Beispiel Wetter oder Kalender