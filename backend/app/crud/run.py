from sqlalchemy.orm import Session
from app.models.run import Run, PlaylistTrack
from datetime import datetime

def get_run_by_strava_id(db: Session, strava_id: str):
    return db.query(Run).filter(Run.strava_activity_id == strava_id).first()

def get_user_runs(db: Session, user_id: int):
    return db.query(Run).filter(Run.user_id == user_id).order_by(Run.start_date.desc()).all()

def create_run_with_tracks(db: Session, user_id: int, run_data: dict, tracks_data: list[dict]):
    # 1. Prepare run object
    start_date_obj = datetime.fromisoformat(run_data['start_date'].replace('Z', '+00:00')).replace(tzinfo=None)
    
    db_run = Run(
        user_id=user_id,
        strava_activity_id=str(run_data['id']),
        name=run_data['name'],
        distance_meters=run_data['distance'],
        elapsed_time_seconds=run_data['elapsed_time'],
        start_date=start_date_obj
    )
    db.add(db_run)
    db.flush() # flush to get the run.id
    
    # 2. Add all matched tracks
    for t in tracks_data:
        played_at_obj = datetime.fromisoformat(t['played_at'].replace('Z', '+00:00')).replace(tzinfo=None)
        
        db_track = PlaylistTrack(
            run_id=db_run.id,
            name=t['name'],
            artist=t['artist'],
            album=t['album'],
            album_image_url=t['album_image_url'],
            duration_ms=t['duration_ms'],
            played_at=played_at_obj,
            external_url=t['external_url']
        )
        db.add(db_track)
        
    db.commit()
    db.refresh(db_run)
    return db_run
