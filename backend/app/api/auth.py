import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.crud.user import create_user, update_strava_tokens, update_spotify_tokens

router = APIRouter()

# --- Strava OAuth ---
@router.get("/strava/login")
def strava_login():
    """Redirect user to Strava's OAuth login page."""
    redirect_uri = "http://localhost:8000/auth/strava/callback"
    url = (f"https://www.strava.com/oauth/authorize?client_id={settings.STRAVA_CLIENT_ID}"
           f"&response_type=code&redirect_uri={redirect_uri}"
           f"&approval_prompt=force&scope=activity:read_all")
    return RedirectResponse(url)

@router.get("/strava/callback")
async def strava_callback(code: str, db: Session = Depends(get_db)):
    """Exchange auth code for access token and save to DB."""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")
    
    # Normally we would identify the user from their session/JWT. 
    # For simplicity, we just create a new user or update an existing one.
    
    # 1. Exchange code for Strava tokens
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": settings.STRAVA_CLIENT_ID,
        "client_secret": settings.STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to authenticate with Strava")
            
        data = response.json()
        
    athlete_id = data['athlete']['id']
    
    # 2. Check if user exists or create new
    # (Here you would link it to db.query to get user. Skipped for brevity, let's just create one for demo!)
    user = create_user(db)
    user.strava_athlete_id = athlete_id
    db.commit()
    
    # 3. Save tokens
    update_strava_tokens(
        db=db, 
        user=user, 
        access_token=data['access_token'], 
        refresh_token=data['refresh_token'], 
        expires_at=data['expires_at']
    )
    
    # 4. Redirect to Frontend Dashboard with some session identifier (e.g. user_id)
    return RedirectResponse(f"http://localhost:5173/dashboard?user_id={user.id}")

# --- Spotify OAuth ---
@router.get("/spotify/login")
def spotify_login(user_id: int):
    """Redirect to Spotify OAuth, passing the user_id as state so we can link it later."""
    redirect_uri = "http://localhost:8000/auth/spotify/callback"
    scopes = "user-read-recently-played"
    
    url = (f"https://accounts.spotify.com/authorize?response_type=code"
           f"&client_id={settings.SPOTIFY_CLIENT_ID}&scope={scopes}"
           f"&redirect_uri={redirect_uri}&state={user_id}")
    return RedirectResponse(url)

@router.get("/spotify/callback")
async def spotify_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Exchange auth code for access token and attach to existing user."""
    # State parameter contains our user_id we passed during login
    user_id = int(state)
    
    # Exchange code
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:8000/auth/spotify/callback",
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=payload, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to authenticate with Spotify")
            
        data = response.json()
        
    # In production, we should calculate expires_at
    import time
    expires_at = int(time.time()) + data['expires_in']
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    update_spotify_tokens(
        db=db,
        user=user,
        access_token=data['access_token'],
        refresh_token=data['refresh_token'],
        expires_at=expires_at
    )
    
    return RedirectResponse(f"http://localhost:5173/dashboard?user_id={user.id}&spotify_connected=true")
