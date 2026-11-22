FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

RUN pip install yt-dlp fastapi uvicorn python-multipart

WORKDIR /app

COPY server.py /app/server.py
COPY index.html /app/index.html

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
