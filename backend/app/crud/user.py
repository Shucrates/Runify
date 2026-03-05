from sqlalchemy.orm import Session
from app.models.user import User

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_strava_id(db: Session, strava_id: int):
    return db.query(User).filter(User.strava_athlete_id == strava_id).first()

def get_user_by_spotify_id(db: Session, spotify_id: str):
    return db.query(User).filter(User.spotify_user_id == spotify_id).first()

def create_user(db: Session):
    db_user = User()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_strava_tokens(db: Session, user: User, access_token: str, refresh_token: str, expires_at: int):
    user.strava_access_token = access_token
    user.strava_refresh_token = refresh_token
    user.strava_token_expires_at = expires_at
    db.commit()
    db.refresh(user)
    return user

def update_spotify_tokens(db: Session, user: User, access_token: str, refresh_token: str, expires_at: int):
    user.spotify_access_token = access_token
    user.spotify_refresh_token = refresh_token
    user.spotify_token_expires_at = expires_at
    db.commit()
    db.refresh(user)
    return user
