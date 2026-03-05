from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Strava Data
    strava_athlete_id = Column(Integer, unique=True, index=True, nullable=True)
    strava_access_token = Column(String, nullable=True)
    strava_refresh_token = Column(String, nullable=True)
    strava_token_expires_at = Column(Integer, nullable=True) # Unix timestamp
    
    # Spotify Data
    spotify_user_id = Column(String, unique=True, index=True, nullable=True)
    spotify_access_token = Column(String, nullable=True)
    spotify_refresh_token = Column(String, nullable=True)
    spotify_token_expires_at = Column(Integer, nullable=True) # Unix timestamp

    created_at = Column(DateTime, default=datetime.utcnow)
