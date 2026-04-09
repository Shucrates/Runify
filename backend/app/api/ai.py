from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import traceback
from app.core.database import get_db
from app.crud.user import get_user
from app.models.run import Run
from app.services.gemini_service import generate_run_summary

router = APIRouter()


@router.post("/summary")
def get_ai_summary(run_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Generate (or return cached) AI summary for a specific run.
    - First call: generates via Gemini, saves to DB, returns result.
    - Subsequent calls: returns the cached summary instantly.
    """
    # Verify user exists
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Load run and verify ownership
    run = db.query(Run).filter(Run.id == run_id, Run.user_id == user_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Return cached summary if available
    if run.ai_summary:
        return {"summary": run.ai_summary, "cached": True}

    # Build track data for the prompt
    tracks = [
        {
            "name": t.name,
            "artist": t.artist,
            "album": t.album,
        }
        for t in run.tracks
    ]

    # Build run data for the prompt
    run_data = {
        "name": run.name,
        "start_date": run.start_date.strftime("%B %d, %Y at %I:%M %p"),
        "distance_meters": run.distance_meters,
        "elapsed_time_seconds": run.elapsed_time_seconds,
    }

    try:
        summary = generate_run_summary(run_data, tracks)
    except Exception as e:
        full_error = traceback.format_exc()
        print("=== GEMINI ERROR ===")
        print(full_error)
        print("===================")
        raise HTTPException(
            status_code=500,
            detail=f"AI generation failed: {str(e)}"
        )

    # Cache the result in DB
    run.ai_summary = summary
    db.commit()

    return {"summary": summary, "cached": False}
