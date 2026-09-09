from faster_whisper import WhisperModel

import sounddevice as sd
import soundfile as sf

import numpy as np
import sys
from evdev import InputDevice, ecodes

from openai import OpenAI
from tools import tools, FUNCTIONS
from dotenv import load_dotenv

import subprocess
import atexit
import json
import re

from database import ConversationDatabase

subprocess.run(['stty', '-echo'])
atexit.register(lambda: subprocess.run(['stty', 'echo']))

load_dotenv()

SAMPLE_RATE = 16000
BLOCK_SIZE = 512

audio_buffer = []
recorded_chunks = []

def callback(indata, frames, time_info, status):
    audio_chunk = indata[:,0]
    audio_buffer.append(audio_chunk.copy())


assistant_speaking = False

whisper_model = WhisperModel("base", "cpu", compute_type="int8")
def transcribe_speech(audio_data):
    global assistant_speaking

    if not assistant_speaking:
        segments, _ = whisper_model.transcribe(audio_data, language="de")
        transcribed_text = " ".join(segment.text for segment in segments)
        # print("\nTranskript: ", transcribed_text)
        return transcribed_text

client = OpenAI()
db = ConversationDatabase()


conversation_history = db.load_history()

def get_response(user_speech):
    if not user_speech:
        return

    conversation_history.append({"role": "user", "content": user_speech})
    db.add_message("user", user_speech) 

    print("Denkt nach...\n")
    
    assistant_response = client.responses.create(
        model="gpt-5.6-sol",
        input=conversation_history,
        tools=tools
    )

    conversation_history.extend(assistant_response.output)

    tool_outputs = []

    for item in assistant_response.output:
        if item.type == "function_call":
            function = FUNCTIONS.get(item.name)
            if function:
                result = function()

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": str(result)
                    }
                )

    if tool_outputs:
        conversation_history.extend(tool_outputs)

        assistant_response = client.responses.create(
            model="gpt-5.6-sol",
            input=conversation_history,
            tools=tools
        )

    assistant_text = assistant_response.output_text

    conversation_history.append({"role": "assistant", "content": assistant_text})
    db.add_message("assistant", assistant_text)
    return assistant_text

def stream_response_to_file(assistant_response, file_path):
    print("Verarbeitet...")

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        input=assistant_response,
        voice="marin"
    ) as response:
        response.stream_to_file(file_path)
        return response

def play_response(file_path: str):
    global assistant_speaking

    assistant_speaking = True
    data, samplerate = sf.read(file_path)
    sd.play(data, samplerate)
    sd.wait()
    assistant_speaking = False

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text

if __name__ == "__main__":

    keyboard = InputDevice("/dev/input/event3")
    key_pressed = False

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        channels=1,
        dtype="float32",
        callback=callback
    )

    try:
        for event in keyboard.read_loop():
            if event.type == ecodes.EV_KEY and event.code == ecodes.KEY_A:
                if event.value == 2 and not key_pressed:
                    key_pressed = True
                    if key_pressed:
                        print("\nRede...\n")
                        stream.start()
                elif event.value == 0:
                    if key_pressed:
                        key_pressed = False

                        stream.stop()
                        print("Aufnahme beendet\n")

                        recorded_chunks = np.concatenate(audio_buffer)
                        audio_buffer.clear()
                        #sd.play(recorded_chunks, samplerate=SAMPLE_RATE)
                        #sd.wait()
                
                        text = transcribe_speech(recorded_chunks)
                        response = get_response(text)
                        stream_response_to_file(response, "response.wav")
                        print("Antwort: ", response)
                        play_response("response.wav")
                        if "okay das war alles" in clean_text(text):
                            stream.stop()
                            stream.close()
                            sys.exit(0)

    except KeyboardInterrupt:
        sys.exit(0)