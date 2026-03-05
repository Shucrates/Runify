import httpx
from fastapi import HTTPException

async def get_recent_runs(access_token: str) -> list[dict]:
    """
    Fetch the authenticated user's recent activities from Strava 
    and filter specifically for runs.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://www.strava.com/api/v3/athlete/activities"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Strava API error: {response.text}"
            )
            
        activities = response.json()
        
        # Filter purely for actual Runs
        runs = [act for act in activities if act.get('type') == 'Run']
        return runs
