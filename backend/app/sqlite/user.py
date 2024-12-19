from pydantic import BaseModel
from dating_plan_ai_agents.mongodb.user_role import UserRole
from datetime import datetime
from typing import Optional, Any


class User(BaseModel):
    index_id: Optional[Any] = None
    name: str
    password: str
    email: str
    age: str
    role: Optional[Any]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
