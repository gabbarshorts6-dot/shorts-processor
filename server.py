from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os
import subprocess
import uuid

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Shorts processor running"}

@app.post("/process")
async def process_video(video_url: str = Form(...)):
    try:
        job_id = str(uuid.uuid4())
        folder = "/app/downloads"
        os.makedirs(folder, exist_ok=True)

        input_file = f"{folder}/{job_id}.mp4"
        output_file = f"{folder}/{job_id}_short.mp4"

        opts = {
            "format": "best[height<=720]/best",
            "outtmpl": input_file,
            "merge_output_format": "mp4",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([video_url])

        subprocess.run([
            "ffmpeg", "-y",
            "-i", input_file,
            "-t", "60",
            "-vf", "crop=min(iw\\,ih*9/16):min(ih\\,iw*16/9):(iw-min(iw\\,ih*9/16))/2:(ih-min(ih\\,iw*16/9))/2,scale=720:1280",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "128k",
            output_file
        ], check=True)

        return FileResponse(
            output_file,
            media_type="video/mp4",
            filename="short.mp4"
        )

    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )
