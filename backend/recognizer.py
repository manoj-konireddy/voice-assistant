import sounddevice as sd
from scipy.io.wavfile import write
import wave
import json
import os
from vosk import Model, KaldiRecognizer


def record_audio(filename, duration=5, fs=44100):
    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, recording)
    print("Recording complete.")


def transcribe_audio(filename):
    if not os.path.exists("model"):
        print("Please download the Vosk model and place it in the 'model' directory.")
        return ""

    model = Model("model")
    wf = wave.open(filename, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())

    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            results.append(result.get("text", ""))
    final_result = json.loads(rec.FinalResult())
    results.append(final_result.get("text", ""))
    return ' '.join(results)
