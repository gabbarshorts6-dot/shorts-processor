from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import yt_dlp
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Shorts processor running"}

@app.post("/process")
async def process_video(video_url: str = Form(...)):
    try:
        os.makedirs("/app/downloads", exist_ok=True)

        opts = {
            "format": "bestvideo[height<=1080]+bestaudio/best",
            "outtmpl": "/app/downloads/video.%(ext)s",
            "merge_output_format": "mp4",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        return JSONResponse({
            "status": "received",
            "title": info.get("title"),
            "message": "Video processing service connected"
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
