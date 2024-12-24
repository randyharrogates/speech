import sys
from pydub import AudioSegment
from fastapi import FastAPI, File, UploadFile
import os
from datetime import datetime
import whisper
import sqlite3
from typing import List
import aiofiles
from backend.app.fastapi.fastapi_helper import load_config, init_db
from backend.app.models.transcription import Transcription


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from frontend
origins = [
    "http://localhost:3000",  # React's default port
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
config = load_config(file_path="backend/app/utils/config.yaml")
DB_NAME = config["database"]["name"]
UPLOAD_FOLDER = config["upload"]["folder"]
MODEL_NAME = config["model"]["name"]
model = whisper.load_model(MODEL_NAME)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
init_db(DB_NAME)


# Health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}


# Transcription endpoint
@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Save uploaded file
    save_path = f"{UPLOAD_FOLDER}/{file.filename}"
    async with aiofiles.open(save_path, "wb") as out_file:
        content = await file.read()  # Read the file content
        await out_file.write(content)

    # Convert audio to WAV format using pydub
    wav_path = f"{UPLOAD_FOLDER}/{os.path.splitext(file.filename)[0]}.wav"
    try:
        audio = AudioSegment.from_file(save_path)
        audio.export(wav_path, format="wav")
    except Exception as e:
        return {"error": f"Audio conversion failed: {str(e)}"}

    # Perform transcription using Whisper
    result = model.transcribe(wav_path)
    transcription = result["text"]

    # Save transcription to database
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO transcriptions (filename, transcription, created_at) VALUES (?, ?, ?)",
        (file.filename, transcription, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

    return {"filename": file.filename, "transcription": transcription}


# Get all transcriptions
@app.get("/transcriptions", response_model=List[Transcription])
def get_transcriptions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT filename, transcription, created_at FROM transcriptions")
    rows = c.fetchall()
    conn.close()

    return [
        {"filename": row[0], "transcription": row[1], "created_at": row[2]}
        for row in rows
    ]


# Search transcriptions by filename
@app.get("/search")
def search_transcriptions(filename: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT filename, transcription, created_at FROM transcriptions WHERE filename LIKE ?",
        ("%" + filename + "%",),
    )
    rows = c.fetchall()
    conn.close()

    return [
        {"filename": row[0], "transcription": row[1], "created_at": row[2]}
        for row in rows
    ]
