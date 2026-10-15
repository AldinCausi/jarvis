from datetime import datetime
from pathlib import Path

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

stop_program_flag = False

def stop_program():
    global stop_program_flag
    stop_program_flag = True

def create_note(title, text_content):
    file_path = Path.home() / f"Schreibtisch/Notizen/{title}.txt"
    with open(file_path, "w") as f:
        f.write(text_content)

    return "Natürlich, sir."

def delete_note(title):
    file_path = Path.home() / f"Schreibtisch/Notizen/{title}.txt"
    file = Path(file_path)
    file.unlink()

    return "Ich habe die Datei gelöscht, sir."

TOOLS = [
    {
        "type": "function",
        "name": "get_current_time",
        "description": "Gibt die aktuelle Uhrzeit zurück.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
    },
    {
        "type": "function",
        "name": "stop_program",
        "description": "Macht Verwendung von der sys Bibliothek von Python, um sys.exit(0) aufzurufen und das Programm zu schließen. Dies soll verwendet werden, wenn der Nutzer dem Assistenten sagt, dass er jetzt nicht mehr gebraucht wird.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
    },
    {
        "type": "function",
        "name": "create_note",
        "description": "Erstellt eine Textdatei. Wenn kein Title gegeben wird, dann denke dir einen aus, der zum Inhalt passt.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Name der Textdatei."
                },
                "text_content": {
                    "type": "string",
                    "description": "Inhalt der Datei."
                }
            },
            "required": ["title", "text_content"]
        }
    },
    {
        "type": "function",
        "name": "delete_note",
        "description": "Löscht die Textdatei.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Name der Datei, die gelöscht werden soll."
                }
            },
            "required": ["title"]
        }
    }
]

FUNCTIONS = {
    "get_current_time": get_current_time,
    "stop_program": stop_program,
    "create_note": create_note,
    "delete_note": delete_note
}