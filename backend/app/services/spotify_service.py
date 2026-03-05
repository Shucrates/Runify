import httpx
from fastapi import HTTPException

async def get_recently_played_tracks(access_token: str, after_timestamp: int = None) -> list[dict]:
    """
    Fetch the user's recently played tracks from Spotify.
    Returns the last 50 tracks.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://api.spotify.com/v1/me/player/recently-played"
    params = {"limit": 50}
    
    if after_timestamp:
        params["after"] = after_timestamp
        
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Spotify API error: {response.text}"
            )
            
        return response.json().get('items', [])
