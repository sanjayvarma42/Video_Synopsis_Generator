from flask import Flask, render_template, request, redirect, url_for, session, flash,send_file, jsonify
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

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")

# Initialize summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

app = Flask(__name__)
CORS(app)

@dataclass(frozen=True)
class VideoInfo:
    id: str
    title: str
    url: str
    duration: int
    channel: str
    channel_url: str

def extract_video_information(url: str) -> VideoInfo:
    ydl_opts = {"quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return VideoInfo(
            id=info_dict.get("id"),
            title=info_dict.get("title"),
            url=info_dict.get("webpage_url"),
            duration=info_dict.get("duration"),
            channel=info_dict.get("channel"),
            channel_url=info_dict.get("channel_url"),
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
    print(f"Downloaded audio as {filename}")
    return filename

def chunk_audio(input_file: str):
    # Ensure sample rate is 16kHz
    sr = librosa.get_samplerate(input_file)
    print(f"Sample rate: {sr}")

    # Stream audio into chunks (30 seconds)
    stream = librosa.stream(
        input_file,
        block_length=60,
        frame_length=16000,
        hop_length=16000
    )

    paths = []
    for i, speech in enumerate(stream):
        fname = f"chunk_{i}.wav"
        sf.write(fname, speech, 16000)
        paths.append(fname)
    print(f"Audio split into {len(paths)} chunks.")
    return paths

def audio_to_text(audio_path):
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return "[Unrecognized speech]"
    except sr.RequestError as e:
        return f"[API error: {e}]"

def transcribe_audio_chunks(chunk_paths):
    full_transcript = ""
    for path in chunk_paths:
        print(f"Transcribing: {path}")
        text = audio_to_text(path)
        full_transcript += text + " "
    return full_transcript.strip()

def summarize_text(text):
    summarized_chunks = []
    chunk_size = 1000
    num_chunks = (len(text) // chunk_size) + 1

    for i in range(num_chunks):
        chunk = text[i * chunk_size:(i + 1) * chunk_size]
        if not chunk.strip():
            continue

        word_count = len(chunk.split())
        max_len = min(100, max(20, int(word_count * 0.6)))
        min_len = min(30, max(5, int(word_count * 0.3)))

        print(f"Summarizing chunk {i+1}/{num_chunks}")
        out = summarizer(chunk, min_length=min_len, max_length=max_len)
        summarized_chunks.append(out[0]['summary_text'])

    return " ".join(summarized_chunks)

@app.route("/")
def home():
    return send_file("home.html")

@app.route('/summarize', methods=['POST'])
def summarize_video():
    try:
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"error": "Missing YouTube URL"}), 400

        video_url = data["url"]
        info = extract_video_information(video_url)

        audio_path = download_audio(video_url)
        chunk_paths = chunk_audio(audio_path)
        transcript = transcribe_audio_chunks(chunk_paths)
        summary = summarize_text(transcript)

        # Cleanup audio chunks
        os.remove(audio_path)
        for path in chunk_paths:
            os.remove(path)

        return jsonify({
            "video_id": info.id,
            "title": info.title,
            "channel": info.channel,
            "transcript": transcript,
            "summary": summary
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to SQLite (make sure you have a user_form table)
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.md5(request.form['password'].encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_form WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = user['email']
            return redirect(url_for('dashboard'))
        else:
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

        hashed_password = hashlib.md5(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_form WHERE email = ?', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Email already exists. Try logging in.')
            conn.close()
            return redirect(url_for('login'))

        cursor.execute('''
            INSERT INTO user_form (fullname, username, phone, email, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (fullname, username, phone, email, hashed_password))
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

@app.route('/home')
def home():
    if 'user' in session:
        return render_template('home.html')  # Make sure you have home.html
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

