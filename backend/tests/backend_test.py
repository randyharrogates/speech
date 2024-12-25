import pytest
from fastapi.testclient import TestClient
from backend.app.fastapi.main import init_db
from backend.app.fastapi.main import app
from io import BytesIO
from unittest.mock import patch, MagicMock
import sqlite3
import sys
import os

# Add the backend directory to the Python path to ensure proper imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

client = TestClient(app)


# Mocked version of the Whisper transcribe function
def mock_transcribe(file_path):
    return {"text": "This is a mock transcription."}


@pytest.fixture(scope="module", autouse=True)
def setup_and_cleanup_db():
    # Ensure the database is initialized before tests run
    init_db("backend/app/utils/test_transcriptions.db")

    # Cleanup after all tests are run
    yield

    # Clean up the database after all tests are done
    conn = sqlite3.connect("backend/app/utils/test_transcriptions.db")
    c = conn.cursor()
    c.execute("DELETE FROM transcriptions")
    conn.commit()
    conn.close()
    # Delete the database file
    if os.path.exists("backend/app/utils/test_transcriptions.db"):
        os.remove("backend/app/utils/test_transcriptions.db")


# Test the health endpoint
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# Test transcribe multiple files with mock data
@patch("backend.app.fastapi.main.model.transcribe", side_effect=mock_transcribe)
def test_transcribe_multiple(mock_transcribe_func):
    # Create dummy audio files in memory using BytesIO
    file_1 = BytesIO(b"dummy_audio_data_1")
    file_1.name = "audio1.mp3"

    file_2 = BytesIO(b"dummy_audio_data_2")
    file_2.name = "audio2.mp3"

    # Send the files to the API
    response = client.post(
        "/transcribe",
        files=[
            ("files", (file_1.name, file_1, "audio/mp3")),
            ("files", (file_2.name, file_2, "audio/mp3")),
        ],
    )

    # Check if the response status is 200
    assert response.status_code == 200
    response_data = response.json()
    assert "transcriptions" in response_data
    assert len(response_data["transcriptions"]) == 2
    assert all("filename" in item for item in response_data["transcriptions"])
    assert all("transcription" in item for item in response_data["transcriptions"])

    # Ensure that the mock transcription function was called
    mock_transcribe_func.assert_called()


# Test getting all transcriptions
def test_get_transcriptions():
    # Insert dummy data into the database for testing
    conn = sqlite3.connect("backend/app/utils/test_transcriptions.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO transcriptions (filename, transcription, created_at) VALUES (?, ?, ?)",
        ("dummy_audio.mp3", "This is a test transcription", "2024-12-19T00:00:00"),
    )
    conn.commit()
    conn.close()

    # Test the /transcriptions endpoint
    response = client.get("/transcriptions")
    assert response.status_code == 200
    response_data = response.json()

    assert isinstance(response_data, list)
    assert len(response_data) > 0
    assert "filename" in response_data[0]
    assert "transcription" in response_data[0]


def test_search_transcriptions():
    # Insert dummy data into the database for searching
    conn = sqlite3.connect("backend/app/utils/test_transcriptions.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO transcriptions (filename, transcription, created_at) VALUES (?, ?, ?)",
        ("search_audio.mp3", "This is a search test", "2024-12-19T00:00:00"),
    )
    conn.commit()
    conn.close()

    # Verify the data exists in the table
    conn = sqlite3.connect("backend/app/utils/test_transcriptions.db")
    c = conn.cursor()
    c.execute("SELECT * FROM transcriptions WHERE filename = ?", ("search_audio.mp3",))
    rows = c.fetchall()
    conn.close()

    assert len(rows) > 0  # Ensure data is inserted into the DB

    # Test the /search endpoint
    response = client.get(
        "/search",
        params={
            "filename": "search_audio",
            "db_name": "backend/app/utils/test_transcriptions.db",
        },
    )
    assert response.status_code == 200
    response_data = response.json()

    # Ensure that we get a non-empty list in response
    assert isinstance(response_data, list)
    assert len(response_data) > 0  # Ensure data is returned
    assert response_data[0]["filename"] == "search_audio.mp3"
    assert "transcription" in response_data[0]
