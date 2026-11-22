
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
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
async def process_video(file: UploadFile = File(...)):
    video_id = str(uuid.uuid4())
    input_file = f"downloads/{video_id}_input"
    output_file = f"downloads/{video_id}_short.mp4"

    try:
        with open(input_file, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                buffer.write(chunk)

        command = [
            "ffmpeg", "-y",
            "-i", input_file,
            "-t", "60",
            "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-movflags", "+faststart",
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
    
