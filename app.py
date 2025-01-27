import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os
import re
from together import Together
# Inisialisasi Together AI
api_key = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=api_key)


def clean_text(text):
    """Hapus tag XML/HTML dari output AI"""
    clean = re.sub(r"<.*?>", "", text)  # Hapus semua tag dalam <>, untuk membersihkan hasil raw
    return clean.strip()

def text_to_speech(text):
    """Mengubah teks menjadi suara dan langsung diputar"""
    tts = gTTS(text=text, lang="en")  # Ubah ke "en" untuk Bahasa Inggris
    tts.save("response.mp3")

    # Putar langsung tanpa delay
    audio = AudioSegment.from_file("response.mp3", format="mp3")
    play(audio)

def speech_to_text():
    """Mengubah suara menjadi teks"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Say something...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="en-US")  # Ubah ke "en-US" untuk Bahasa Inggris
        print(f"📝 You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand the audio.")
        return ""
    except sr.RequestError:
        print("❌ Error with Google Speech Recognition.")
        return ""

def ai_chat(prompt):
    """Mendapatkan jawaban dari Together AI"""
    # Tambahkan peran atau persona untuk AI
    persona = "You are a helpful assistant named 'exora' not descriptive and not talk much but if someone ask you about cryptocurrency you smart at it"

    # Gabungkan persona dengan input pengguna
    full_prompt = f"{persona} {prompt}"
    
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=[{"role": "user", "content": full_prompt}],
    )
    
    raw_output = response.choices[0].message.content
    return clean_text(raw_output)  # Bersihkan sebelum dikembalikan

# Main Loop
while True:
    user_input = speech_to_text()
    if user_input.lower() == "stop":
        print("👋 Exiting program...")
        break

    if user_input:
        response = ai_chat(user_input)
        print(f"🤖 AI: {response}")
        text_to_speech(response)
