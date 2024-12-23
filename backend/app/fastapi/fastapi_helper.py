# backend/main.py
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from datetime import datetime
import whisper
import sqlite3
from typing import List
import os
import aiofiles
import yaml


def load_config(file_path="config.yaml"):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def init_db(DB_NAME):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS transcriptions
                 (id INTEGER PRIMARY KEY, filename TEXT, transcription TEXT, created_at TEXT)"""
    )
    conn.commit()
    conn.close()
