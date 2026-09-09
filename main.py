from faster_whisper import WhisperModel
from silero_vad import load_silero_vad
import torch

import sounddevice as sd
import soundfile as sf

import numpy as np
import sys

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SAMPLE_RATE = 16000
BLOCK_SIZE = 512

audio_buffer = []
recorded_chunks = []

model = load_silero_vad()

def is_speech(audio_data: np.ndarray, sample_rate=SAMPLE_RATE, threshold=0.5) -> bool:
    audio_tensor = torch.from_numpy(audio_data)
    speech_prob = model(audio_tensor, sample_rate).item()
    return speech_prob > threshold

def callback(indata, frames, time_info, status):
    audio_chunk = indata[:,0]
    if is_speech(audio_chunk):
        print("Speech detected")
        audio_buffer.append(audio_chunk.copy())
    else:
        audio_buffer.append(audio_chunk.copy())
        print("Silence detected")

assistant_speaking = False

whisper_model = WhisperModel("small", "cpu", compute_type="int8")
def transcribe_speech(audio_data):
    global assistant_speaking

    if not assistant_speaking:
        segments, info = whisper_model.transcribe(audio_data, language="de")
        transcribed_text = " ".join(segment.text for segment in segments)
        print("Transkript: ", transcribed_text)
        return transcribed_text

client = OpenAI()

def get_response(user_speech):
    if not user_speech:
        return
    assistant_response = client.responses.create(
        model="gpt-5.6-luna",
        input=user_speech
    )

    return assistant_response.output_text

def stream_response_to_file(assistant_response, file_path):
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

if __name__ == "__main__":
    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, channels=1, dtype="float32", callback=callback):
            while True:
                sd.sleep(100)
            
    except KeyboardInterrupt:
        recorded_chunks = np.concatenate(audio_buffer)
        sd.play(recorded_chunks, samplerate=SAMPLE_RATE)
        sd.wait()
        text = transcribe_speech(recorded_chunks)
        response = get_response(text)
        stream_response_to_file(response, "response.wav")
        play_response("response.wav")

        sys.exit(0)