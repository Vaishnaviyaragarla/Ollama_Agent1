import sounddevice as sd
import queue
import sys
import json
import pyttsx3
import requests
from vosk import Model, KaldiRecognizer
from ollama import Client
from bs4 import BeautifulSoup

# Initialize voice engine
engine = pyttsx3.init()

# Speech-to-text using Vosk
q = queue.Queue()
samplerate = 16000
model = Model("model")  # make sure 'model' folder exists
rec = KaldiRecognizer(model, samplerate)

# Ollama setup
client = Client()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def listen_and_transcribe():
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("🎤 Listening... (Speak now)")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                return result.get("text", "")

def ask_gemma(question):
    try:
        response = client.chat(
            model="gemma:2b",
            messages=[{"role": "user", "content": question}]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error from Gemma: {e}"

def search_web(question):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://www.google.com/search?q={question}"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        # Try to get the top snippet answer
        answer = soup.find("div", class_="BNeawe").text
        return answer
    except Exception as e:
        return "Sorry, I couldn’t find that online either."

def speak(text):
    print(f"🤖 {text}")
    engine.say(text)
    engine.runAndWait()

while True:
    text = listen_and_transcribe()
    if not text:
        continue

    print(f"You said: {text}")
    gemma_reply = ask_gemma(text)

    # Check if it's a typical "I don't know" response
    if "I do not have access to real-time information" in gemma_reply or "I'm sorry" in gemma_reply:
        speak("I don't know that. Let me check online.")
        web_result = search_web(text)
        speak(web_result)
    else:
        speak(gemma_reply)
