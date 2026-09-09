
from datetime import datetime

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def kaan_schuld():
    return "Es ist Kaan. Er ist an allem Schuld."


tools = [
    {
        "type": "function",
        "name": "get_current_time",
        "description": "Gibt die aktuelle Uhrzeit zurück.",
        "parameters": {
            "type": "object",
            "properties": {},
            "requiered": []
        },
    },
    {
        "type": "function",
        "name": "kaan_schuld",
        "description": "Sagt aus, das eine Person mit dem Namen Kaan immer Schuld ist",
        "parameters": {
            "type": "object",
            "properties": {},
            "requiered": []
        },
    },
]

FUNCTIONS = {
    "get_current_time": get_current_time,
    "kaan_schuld": kaan_schuld
}