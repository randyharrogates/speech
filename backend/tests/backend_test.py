import pytest
from fastapi.testclient import TestClient
from app.fastapi.main import app
from unittest.mock import patch
import os

# Test Client
client = TestClient(app)


# 1. Test the health endpoint
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# 2. Test transcription endpoint with a mock Whisper model
@pytest.mark.asyncio
@patch("backend.main.model.transcribe")
@patch("aiofiles.open")
async def test_transcribe(mock_open, mock_transcribe):
    # Mock the transcription result
    mock_transcribe.return_value = {"text": "This is a test transcription."}

    # Mock file saving process
    mock_open.return_value.__aenter__.return_value.write = lambda x: None  # No-op

    # Send a mock file to the transcribe endpoint
    with open("test_audio.mp3", "wb") as f:
        response = client.post(
            "/transcribe", files={"file": ("test_audio.mp3", f, "audio/mp3")}
        )

    # Check if the response contains the expected transcription
    assert response.status_code == 200
    assert response.json() == {
        "filename": "test_audio.mp3",
        "transcription": "This is a test transcription.",
    }

    # Check if the Whisper model was called
    mock_transcribe.assert_called_once()


# 3. Test search transcriptions endpoint
@pytest.mark.asyncio
@patch("sqlite3.connect")
def test_search_transcriptions(mock_connect):
    # Mock database response
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [
        ("test_audio.mp3", "This is a test transcription.", "2024-12-19T12:00:00")
    ]

    # Perform a search query
    response = client.get("/search?filename=test_audio")

    # Check the response
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["filename"] == "test_audio.mp3"
    assert response.json()[0]["transcription"] == "This is a test transcription."
    assert response.json()[0]["created_at"] == "2024-12-19T12:00:00"

    # Check if the database was queried correctly
    mock_cursor.execute.assert_called_once_with(
        "SELECT filename, transcription, created_at FROM transcriptions WHERE filename LIKE ?",
        ("%test_audio%",),
    )
