from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Strava info
    strava_activity_id = Column(String, unique=True, index=True)
    name = Column(String)
    distance_meters = Column(Float)
    elapsed_time_seconds = Column(Integer)
    start_date = Column(DateTime)
    ai_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="runs")
    tracks = relationship("PlaylistTrack", back_populates="run", cascade="all, delete")


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"))
    
    # Spotify info
    name = Column(String)
    artist = Column(String)
    album = Column(String)
    album_image_url = Column(String)
    duration_ms = Column(Integer)
    played_at = Column(DateTime)
    external_url = Column(String)

    run = relationship("Run", back_populates="tracks")
