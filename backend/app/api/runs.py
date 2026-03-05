from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.user import get_user
from app.crud.run import get_user_runs, get_run_by_strava_id, create_run_with_tracks
from app.services.strava_service import get_recent_runs
from app.services.spotify_service import get_recently_played_tracks
from app.utils.matching import match_songs_to_run

router = APIRouter()

@router.post("/sync")
async def sync_runs_and_music(user_id: int, db: Session = Depends(get_db)):
    """
    Fetches recent runs from Strava, recently played tracks from Spotify,
    matches them together, and saves any new runs to the database.
    """
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not user.strava_access_token or not user.spotify_access_token:
        raise HTTPException(
            status_code=400, 
            detail="User must connect both Strava and Spotify before syncing."
        )

    # 1. Fetch from Strava & Spotify simultaneously
    try:
        strava_runs = await get_recent_runs(user.strava_access_token)
        spotify_tracks = await get_recently_played_tracks(user.spotify_access_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    synced_runs = []
    
    # 2. Iterate through runs and match
    for run_data in strava_runs:
        activity_id = str(run_data['id'])
        
        # Skip if we already processed this run
        existing_run = get_run_by_strava_id(db, activity_id)
        if existing_run:
            continue
            
        # Match tracks to this specific run
        matched_tracks = match_songs_to_run(run_data, spotify_tracks)
        
        # Save to database
        new_run = create_run_with_tracks(db, user_id, run_data, matched_tracks)
        synced_runs.append({
            "run_name": new_run.name,
            "tracks_matched": len(matched_tracks)
        })
        
    return {
        "message": "Sync complete",
        "new_runs_synced": len(synced_runs),
        "details": synced_runs
    }

@router.get("/")
def get_runs(user_id: int, db: Session = Depends(get_db)):
    """Retrieve all previously synced runs and their tracks for the dashboard."""
    runs = get_user_runs(db, user_id)
    
    # Format response for the frontend
    response = []
    for r in runs:
        response.append({
            "id": r.id,
            "strava_activity_id": r.strava_activity_id,
            "name": r.name,
            "distance_meters": r.distance_meters,
            "elapsed_time_seconds": r.elapsed_time_seconds,
            "start_date": r.start_date.isoformat(),
            "tracks": [
                {
                    "name": t.name,
                    "artist": t.artist,
                    "album": t.album,
                    "album_image_url": t.album_image_url,
                    "duration_ms": t.duration_ms,
                    "played_at": t.played_at.isoformat(),
                    "external_url": t.external_url
                } for t in r.tracks
            ]
        })
        
    return response
