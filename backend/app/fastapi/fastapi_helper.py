# backend/main.py

import sqlite3
from typing import List
import yaml


def load_config(file_path: str = "config.yaml"):
    """
    Loads a YAML configuration file and returns it as a dictionary.

    Args:
        file_path (str): The path to the YAML configuration file to load.

    Returns:
        dict: The loaded configuration as a dictionary.
    """
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def init_db(DB_NAME: str):
    """
    Initializes a SQLite database with the given name.

    The database is created if it does not already exist. A table named
    "transcriptions" is created if it does not already exist. The table has the
    following columns:

    - id: A unique integer identifier for the row, automatically incremented.
    - filename: The name of the audio file that was transcribed.
    - transcription: The transcription of the audio file.
    - created_at: The time the audio file was transcribed.

    Args:
        DB_NAME (str): The name of the SQLite database to initialize.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS transcriptions
                 (id INTEGER PRIMARY KEY, filename TEXT, transcription TEXT, created_at TEXT)"""
    )
    conn.commit()
    conn.close()
