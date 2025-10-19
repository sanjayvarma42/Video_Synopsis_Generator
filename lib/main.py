from flask import Flask, request, jsonify
from dataclasses import dataclass
import yt_dlp
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled
)
from transformers import pipeline
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load summarization model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

@dataclass(frozen=True)
class VideoInfo:
    id: str
    title: str
    url: str
    duration: int
    channel: str
    channel_url: str

def extract_video_info(url: str) -> VideoInfo:
    ydl_opts = {"quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return VideoInfo(
            id=info.get("id"),
            title=info.get("title"),
            url=info.get("webpage_url"),
            duration=info.get("duration"),
            channel=info.get("channel"),
            channel_url=info.get("channel_url"),
        )

def get_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."

    try:
        transcript = transcript_list.find_manually_created_transcript(["en"])
    except NoTranscriptFound:
        try:
            transcript = transcript_list.find_generated_transcript(["en"])
        except NoTranscriptFound:
            return "No English transcript available for this video."

    subtitles = transcript.fetch()
    if not subtitles:
        return "Failed to fetch transcript data or transcript data is empty."

    # Combine into paragraphs every ~4 lines
    lines = [sbt.text for sbt in subtitles if sbt.text != "[Music]"]
    paragraphs = [" ".join(lines[i:i+4]) for i in range(0, len(lines), 4)]

    return "\n\n".join(paragraphs)

def summarize_text(text):
    summarized_text = []
    num_iters = int(len(text) / 1000)
    print(f"Summarizing in {num_iters + 1} chunks...")

    for i in range(0, num_iters + 1):
        chunk = text[i * 1000: (i + 1) * 1000]
        if not chunk.strip():
            continue

        input_length = len(chunk.split())
        max_len = min(100, max(20, int(input_length * 0.6)))
        min_len = min(30, max(5, int(input_length * 0.3)))

        print(f"Chunk {i+1}/{num_iters+1}: summarizing {input_length} words...")
        out = summarizer(chunk, min_length=min_len, max_length=max_len)
        summarized_text.append(out[0]['summary_text'])

    print("Summarization complete.")
    return " ".join(summarized_text)

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "Missing YouTube URL"}), 400

        video_url = data['url']
        info = extract_video_info(video_url)
        transcript = get_transcript(info.id)

        if "Transcript not available" in transcript:
            summary = "Summary not available due to missing transcript."
        else:
            summary = summarize_text(transcript)

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
