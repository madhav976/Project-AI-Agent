import sounddevice as sd
from faster_whisper import WhisperModel
from google import genai
from scipy.io.wavfile import write
import time
import subprocess
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = WhisperModel("base")

def speak(text):
    print("Speaking:", text)
    subprocess.run([
        "powershell", "-Command",
        f'Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak("{text}")'
    ])

def save_to_file(role, text):
    f = open("chat_history.txt", "a")
    f.write(role + ": " + text + "\n")
    f.close()

chat_log = ""

def ask_gemini(user_text):
    global chat_log
    chat_log = chat_log + "User: " + user_text + "\n"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=chat_log
    )
    ai_reply = response.text.replace("\n", " ")
    chat_log = chat_log + "AI: " + ai_reply + "\n"
    return ai_reply

if __name__ == "__main__":
    speak("Hello, I am Ready")

    while True:   
        print("\nRecording...")
        sample_rate = 44100
        duration = 5

        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1
        )
        sd.wait()
        sd.stop()
        time.sleep(0.5)

        print("Transcribing...")
        write("recording.wav", sample_rate, audio)

        segments, info = model.transcribe("recording.wav")

        for segment in segments:
            user_text = segment.text
            print("You:", user_text)
            save_to_file("User", user_text)

            try:
                ai_reply = ask_gemini(user_text)  # 👈 now actually using the function
                print("AI:", ai_reply)
                speak(ai_reply)
                save_to_file("AI", ai_reply)

            except Exception as e:
                print("Gemini Error:", e)