import os
import re
import uuid
import base64
import tempfile
import subprocess
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

def normalize_url(url):
    url = url.strip()
    shorts_match = re.match(r'https?://(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]+)', url)
    if shorts_match:
        video_id = shorts_match.group(1)
        return f"https://www.youtube.com/watch?v={video_id}"
    return url

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    raw_url = data.get("url", "").strip()
    if not raw_url:
        return jsonify({"error": "No URL provided."}), 400

    url = normalize_url(raw_url)

    tmp_dir = tempfile.mkdtemp()
    output_template = os.path.join(tmp_dir, "%(title)s.%(ext)s")

    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "--merge-output-format", "mp4",
                "--output", output_template,
                "--no-playlist",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            return jsonify({"error": result.stderr or "Download failed."}), 500

        files = [f for f in os.listdir(tmp_dir) if f.endswith(".mp4")]
        if not files:
            return jsonify({"error": "No MP4 file produced."}), 500

        filepath = os.path.join(tmp_dir, files[0])
        filename = files[0]

        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

    finally:
        for f in os.listdir(tmp_dir):
            try:
                os.remove(os.path.join(tmp_dir, f))
            except Exception:
                pass
        try:
            os.rmdir(tmp_dir)
        except Exception:
            pass

    return jsonify({"filename": filename, "data": encoded})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
