from fastapi import FastAPI, File, UploadFile, HTTPException
import os
import yaml
import logging.config
from datetime import datetime
import whisper
import sqlite3
from typing import List
import aiofiles
from backend.app.fastapi.fastapi_helper import load_config, init_db
from backend.app.models.transcription import Transcription
from fastapi.middleware.cors import CORSMiddleware

# Load logging configuration from logging.yaml
with open("backend/app/utils/logging.yaml", "r") as file:
    config = yaml.safe_load(file)
    logging.config.dictConfig(config)

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
    """
    Simple health endpoint that always returns a 200 response with a JSON object of {'status': 'ok'}.
    """
    logging.info("Health endpoint accessed")
    return {"status": "ok"}


@app.post("/transcribe")
async def transcribe_multiple(files: list[UploadFile] = File(...)):
    """
    Transcribes multiple audio files uploaded by the user.

    This endpoint accepts a list of audio files, saves each file to the
    server, performs transcription using the Whisper model, and stores the
    results in a SQLite database. The transcriptions are returned as a JSON
    response containing the filename and transcription text.

    Args:
        files (list[UploadFile]): List of audio files to be transcribed.

    Returns:
        dict: A JSON object containing a list of transcriptions, each with
        a filename and its corresponding transcription. In case of an error
        during transcription, an error message is returned.
    """

    transcriptions = []

    for file in files:
        logging.info(f"Transcribing file: {file.filename}")

        # Save uploaded file
        save_path = f"{UPLOAD_FOLDER}/{file.filename}"
        async with aiofiles.open(save_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
        logging.info(f"File saved to {save_path}")

        try:
            # Perform transcription using Whisper model
            result = model.transcribe(save_path)
            transcription = result["text"]

            # Log the transcription result
            logging.info(f"Transcription for {file.filename}: {transcription}")
        except Exception as e:
            logging.error(f"Audio transcription failed for {file.filename}: {str(e)}")
            return {
                "error": f"Audio transcription failed for {file.filename}: {str(e)}"
            }

        # Save transcription to the database
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute(
                "INSERT INTO transcriptions (filename, transcription, created_at) VALUES (?, ?, ?)",
                (file.filename, transcription, datetime.now().isoformat()),
            )
            conn.commit()
            conn.close()
            logging.info(f"Transcription for {file.filename} saved to the database")
        except sqlite3.Error as e:
            logging.error(f"Database error: {str(e)}")
            return {"error": f"Database error: {str(e)}"}

        # Append result to the list of transcriptions
        transcriptions.append(
            {"filename": file.filename, "transcription": transcription}
        )

    return {"transcriptions": transcriptions}


@app.get("/transcriptions", response_model=List[Transcription])
def get_transcriptions():
    """
    Retrieves all transcriptions from the database.

    Returns:
        List[Transcription]: A list of transcriptions, each containing the filename,
        transcription text, and the time the transcription was created.

    Raises:
        HTTPException: If there is an error while fetching data from the database.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT filename, transcription, created_at FROM transcriptions")
        rows = c.fetchall()
        conn.close()

        # If no transcriptions are found
        if not rows:
            logging.info("No transcriptions found in the database.")
            raise HTTPException(status_code=404, detail="No transcriptions found.")

        logging.info(f"Retrieved {len(rows)} transcriptions.")
        return [
            {"filename": row[0], "transcription": row[1], "created_at": row[2]}
            for row in rows
        ]
    except sqlite3.Error as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/search")
def search_transcriptions(filename: str, db_name: str = DB_NAME):
    """
    Searches for transcriptions by filename.

    Args:
        filename (str): The search query to look for in the filename.
        db_name (str, optional): The name of the database to search in. Defaults to DB_NAME.

    Returns:
        List[Transcription]: A list of transcriptions, each containing the filename,
        transcription text, and the time the transcription was created.

    Raises:
        HTTPException: If there is an error while performing the search or connecting to the database.
    """
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(
            "SELECT filename, transcription, created_at FROM transcriptions WHERE filename LIKE ?",
            ("%" + filename + "%",),
        )

        rows = c.fetchall()
        conn.close()

        # If no results are found for the search
        if not rows:
            logging.info(f"No transcriptions found for filename: {filename}")
            raise HTTPException(
                status_code=404,
                detail="No transcriptions found matching the search criteria.",
            )

        logging.info(f"Found {len(rows)} transcriptions matching {filename}.")
        return [
            {"filename": row[0], "transcription": row[1], "created_at": row[2]}
            for row in rows
        ]
    except sqlite3.Error as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
