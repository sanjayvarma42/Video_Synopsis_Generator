# 🎬 Video Synopsis Generator

**Video Synopsis Generator** is a cross-platform application available on **Web**, **Android (Flutter)**, and as a **Browser Extension**. It enables users to generate concise summaries of YouTube videos using cutting-edge Natural Language Processing (NLP) techniques.

Whether you're a student, researcher, or content consumer, this tool helps you quickly grasp the essence of long videos by analyzing transcripts or audio and summarizing them in real-time.

---
## 👤 Team

Bathini Raja Rajeshwar      - 22SS1A6606

Karupakala Sai Manas        - 22SS1A6624

Namepalli Sanjay Varma      - 22SS1A6642

Velpula Abhinay             - 22SS1A6659



## ✨ Key Features

- 🔗 Accepts YouTube video URL
- 🧠 Extracts transcript or applies **Automatic Speech Recognition (ASR)** via Whisper
- 📃 Uses **T5, BART** transformer models for accurate summarization
- ⚙️ Backend pipeline handles everything from audio download to final summary
- 🌐 Available on Web, Android (Flutter), and as a Browser Extension
- ⚡ Real-time processing and clear, human-readable output

---

## 🏗️ Architecture Overview

User Input (YouTube URL)




[ Flask Backend ]


├── yt-dlp: Extract Transcript or Audio

├── Whisper: Transcribe Audio if Needed

└── NLP: T5 / BART 



---

## 🖥️ Platforms

- ✅ **Web App** – React frontend for desktop & mobile browsers
- ✅ **Android App** – Built with Flutter
- ✅ **Browser Extension** – One-click summaries while browsing YouTube

---

## 🔧 Technologies Used

### 🔙 Backend (Python Flask)
- `yt-dlp` – Download transcripts or audio
- `Whisper` – Automatic Speech Recognition (ASR)
- `Transformers` – Pretrained NLP models: T5, BART, Pegasus
- `Flask` – REST API server

### 📱 Frontend
- **Flutter** – Android App
- **React** – Web App
- **JavaScript / HTML / CSS** – Browser Extension

---

## 🚀 Getting Started

### 📦 Prerequisites

- Python 3.8+
- Node.js (for Web App)
- Flutter SDK (for Android)
- Git, pip, virtualenv

### 🖥️ Backend Setup

```bash

git clone https://github.com/sanjayvarma42/video-synopsis-generator.git

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 📱 Flutter (Android App)
```bash
cd flutter_app
flutter pub get
flutter run
```

### 🌐 Web App
```bash
cd web_app
npm install
npm start
```

### 🧪 Example Usage
```
Open the app (web, mobile, or extension).

Paste a YouTube video URL.

Click Summarize.

Get a clean, AI-generated summary within seconds.
```


### 📸 Screenshots

#### Website
![image](https://github.com/user-attachments/assets/814c6106-6de1-4a85-84a0-2428e73a2875)


#### Extension


![image](https://github.com/user-attachments/assets/53a25553-7e38-466e-8b28-07e072862cea)



#### Android App


![image](https://github.com/user-attachments/assets/e2f79c77-ab8a-40e5-8397-7faa36f576d8)

### 🧠 Models Used
```
Whisper (OpenAI): for ASR when transcript isn't available

T5 (Text-To-Text Transfer Transformer): for general-purpose summarization

BART (Facebook AI): for abstractive summarization

```

### 🙏 Acknowledgements
```
OpenAI Whisper

Hugging Face Transformers

yt-dlp

Flutter

React

yaml

---
```
