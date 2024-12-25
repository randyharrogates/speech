import sys
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
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = load_config(file_path="backend/app/utils/config.yaml")
DB_NAME = config["database"]["name"]
UPLOAD_FOLDER = config["upload"]["folder"]
MODEL_NAME = config["model"]["name"]
model = whisper.load_model(MODEL_NAME)

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize database
init_db(DB_NAME)

# Health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/transcribe")
async def transcribe_multiple(files: list[UploadFile] = File(...)):
    transcriptions = []

    for file in files:
        # Save uploaded file
        save_path = f"{UPLOAD_FOLDER}/{file.filename}"
        async with aiofiles.open(save_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        # Perform transcription using Whisper (directly pass the file without conversion)
        try:
            result = model.transcribe(
                save_path
            )  # Assuming Whisper supports the file format
            transcription = result["text"]
        except Exception as e:
            return {
                "error": f"Audio transcription failed for {file.filename}: {str(e)}"
            }

        # Save transcription to database
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO transcriptions (filename, transcription, created_at) VALUES (?, ?, ?)",
            (file.filename, transcription, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

        # Append result to the list of transcriptions
        transcriptions.append(
            {"filename": file.filename, "transcription": transcription}
        )

    return {"transcriptions": transcriptions}


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


@app.get("/search")
def search_transcriptions(filename: str, db_name: str = DB_NAME):
    conn = sqlite3.connect(db_name)
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
