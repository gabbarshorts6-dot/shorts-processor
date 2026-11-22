from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import yt_dlp
import os
import subprocess
import uuid

app = FastAPI()

BASE = "/app/downloads"
os.makedirs(BASE, exist_ok=True)

COOKIE_FILE = "/etc/secrets/youtube_cookies.txt"

@app.get("/", response_class=HTMLResponse)
def home():
    with open("/app/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/process")
async def process_video(video_url: str = Form(...)):
    try:
        job_id = str(uuid.uuid4())
        folder = os.path.join(BASE, job_id)
        os.makedirs(folder, exist_ok=True)

        source = os.path.join(folder, "source.mp4")
        output = os.path.join(folder, "short.mp4")

        opts = {
            "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "outtmpl": source,
            "merge_output_format": "mp4",
            "quiet": True,
        }

        if os.path.isfile(COOKIE_FILE):
            opts["cookiefile"] = COOKIE_FILE

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([video_url])

        subprocess.run([
            "ffmpeg", "-y", "-i", source,
            "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
            "-c:v", "libx264", "-preset", "fast",
            "-crf", "23", "-c:a", "aac",
            "-b:a", "128k", output
        ], check=True)

        return JSONResponse({
            "status": "success",
            "message": "Short ready!",
            "download_url": f"/download/{job_id}"
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/download/{job_id}")
def download_short(job_id: str):
    path = os.path.join(BASE, job_id, "short.mp4")

    if not os.path.isfile(path):
        return JSONResponse({"error": "File not found"}, status_code=404)

    return FileResponse(path, media_type="video/mp4", filename="short.mp4")
