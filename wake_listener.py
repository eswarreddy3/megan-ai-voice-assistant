# wake_listener.py
from vosk import Model, KaldiRecognizer
import pyaudio
import json

def wait_for_wake_word(trigger_words=["hey"]):
    model = Model("vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)
    mic = pyaudio.PyAudio()

    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000,
                      input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("🔎 Waiting for wake word...")

    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            text = json.loads(result)["text"]
            if any(w in text for w in trigger_words):
                print("🎤 Wake word detected:", text)
                return  # Exit loop and let main take over
