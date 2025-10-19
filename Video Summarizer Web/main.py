from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from flask_cors import CORS
from dataclasses import dataclass
import os
import torch
import yt_dlp
import librosa
import soundfile as sf
import speech_recognition as sr
from transformers import pipeline
import sqlite3
import hashlib

# Device selection
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")

# Summarizer pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Flask app setup
app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'

@dataclass(frozen=True)
class VideoInfo:
    id: str
    title: str
    url: str
    duration: int
    channel: str
    channel_url: str

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def extract_video_information(url: str) -> VideoInfo:
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return VideoInfo(
            id=info["id"],
            title=info["title"],
            url=info["webpage_url"],
            duration=info["duration"],
            channel=info["channel"],
            channel_url=info["channel_url"]
        )

def download_audio(video_url: str, filename="ytaudio.wav"):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": filename,
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    return filename

def chunk_audio(input_file: str):
    sr = librosa.get_samplerate(input_file)
    stream = librosa.stream(input_file, block_length=60, frame_length=16000, hop_length=16000)
    chunks = []
    for i, segment in enumerate(stream):
        fname = f"chunk_{i}.wav"
        sf.write(fname, segment, 16000)
        chunks.append(fname)
    return chunks

def audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "[Unrecognized speech]"
    except sr.RequestError as e:
        return f"[Speech API error: {e}]"

def transcribe_audio_chunks(paths):
    transcript = ""
    for path in paths:
        transcript += audio_to_text(path) + " "
    return transcript.strip()

def summarize_text(text):
    summaries = []
    chunk_size = 1000
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        if chunk.strip():
            summary = summarizer(chunk, min_length=30, max_length=100)[0]['summary_text']
            summaries.append(summary)
    return " ".join(summaries)

# Routes

@app.route('/summarize', methods=['POST'])
def summarize_video():
    try:
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"error": "Missing YouTube URL"}), 400

        video_url = data["url"]
        info = extract_video_information(video_url)
        audio_path = download_audio(video_url)
        chunks = chunk_audio(audio_path)
        transcript = transcribe_audio_chunks(chunks)
        summary = summarize_text(transcript)

        os.remove(audio_path)
        for c in chunks:
            os.remove(c)

        return jsonify({
            "video_id": info.id,
            "title": info.title,
            "channel": info.channel,
            "transcript": transcript,
            "summary": summary
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.md5(request.form['password'].encode()).hexdigest()

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM user_form WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()

        if user:
            session['user'] = user['email']
            return redirect(url_for('dashboard'))
        flash('Incorrect email or password!')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['cpassword']

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('register'))

        hashed = hashlib.md5(password.encode()).hexdigest()
        conn = get_db_connection()
        cursor = conn.cursor()
        if cursor.execute('SELECT * FROM user_form WHERE email = ?', (email,)).fetchone():
            flash('Email already exists!')
            conn.close()
            return redirect(url_for('login'))

        cursor.execute('''INSERT INTO user_form (fullname, username, phone, email, password)
                          VALUES (?, ?, ?, ?, ?)''',
                       (fullname, username, phone, email, hashed))
        conn.commit()
        conn.close()

        flash('Registration successful! Please log in.')
        return redirect(url_for('success'))

    return render_template('register.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Fallback homepage
@app.route('/')
def root():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
