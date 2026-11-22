from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp
import subprocess
import os
import uuid

app = FastAPI()

os.makedirs("downloads", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/process")
def process_video(url: str = Form(...)):
    video_id = str(uuid.uuid4())
    input_file = f"downloads/{video_id}.mp4"
    output_file = f"downloads/{video_id}_short.mp4"

    try:
        options = {
            "format": "best[height<=720]/best",
            "outtmpl": input_file,
            "noplaylist": True,
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        if not os.path.exists(input_file):
            return {"error": "Video download failed."}

        command = [
            "ffmpeg", "-y",
            "-i", input_file,
            "-t", "60",
            "-vf",
            "crop=min(iw\\,ih*9/16):ih:(iw-min(iw\\,ih*9/16))/2:0,scale=720:1280",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            output_file
        ]

        subprocess.run(command, check=True, capture_output=True)

        return {
            "success": True,
            "download_url": f"/download/{video_id}"
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(input_file):
            os.remove(input_file)

@app.get("/download/{video_id}")
def download_video(video_id: str):
    path = f"downloads/{video_id}_short.mp4"

    if not os.path.exists(path):
        return {"error": "File not found"}

    return FileResponse(
        path,
        media_type="video/mp4",
        filename="short.mp4"
    )
