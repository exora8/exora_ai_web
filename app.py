from flask import Flask, request, jsonify
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os
import re
from together import Together

# Inisialisasi Flask
app = Flask(__name__)

# Inisialisasi Together AI
client = Together(api_key="4eb3afd18344fdf6c699280f9e5e2f08ba5d4c2cc9989b55e7c5c14910af9706")

def clean_text(text):
    """Hapus tag XML/HTML dari output AI"""
    clean = re.sub(r"<.*?>", "", text)
    return clean.strip()

def text_to_speech(text):
    """Mengubah teks menjadi suara dan menyimpannya sebagai file"""
    tts = gTTS(text=text, lang="en")
    tts.save("response.mp3")
    return "response.mp3"

def speech_to_text(audio_file):
    """Mengubah file suara menjadi teks"""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio, language="en-US")
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError:
        return "Error with Google Speech Recognition."

def ai_chat(prompt):
    """Mendapatkan jawaban dari Together AI"""
    persona = "You are a helpful assistant named 'Exora' not descriptive and not talk much but smart at cryptocurrency"
    full_prompt = f"{persona} {prompt}"
    
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=[{"role": "user", "content": full_prompt}],
    )
    
    return clean_text(response.choices[0].message.content)

@app.route('/')
def home():
    return "Exora AI is running!"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get("text")
    
    if not user_input:
        return jsonify({"error": "No text provided"}), 400

    response = ai_chat(user_input)
    return jsonify({"response": response})

@app.route('/speech-to-text', methods=['POST'])
def convert_speech_to_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    file_path = "input.wav"
    file.save(file_path)
    
    text = speech_to_text(file_path)
    os.remove(file_path)
    
    return jsonify({"text": text})

@app.route('/text-to-speech', methods=['POST'])
def convert_text_to_speech():
    data = request.get_json()
    text = data.get("text")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    audio_file = text_to_speech(text)
    return jsonify({"audio": audio_file})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
