from pydantic import BaseModel

class Transcription(BaseModel):
    filename: str
    transcription: str
    created_at: str