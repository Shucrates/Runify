from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    pass

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    strava_athlete_id: Optional[int] = None
    spotify_user_id: Optional[str] = None
    created_at: datetime
    
    # We purposefully exclude access/refresh tokens from the response 
    # to avoid leaking secrets to the frontend.

    class Config:
        from_attributes = True
