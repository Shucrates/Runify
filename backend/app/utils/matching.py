from datetime import datetime, timedelta

def match_songs_to_run(run: dict, recently_played_tracks: list[dict]) -> list[dict]:
    """
    Given a Strava run dict and a list of Spotify recently played tracks,
    returns the tracks that were playing at any point during the run.
    """
    # Parse Strava timestamps (Strava's start_date is in UTC ISO 8601)
    run_start = datetime.fromisoformat(run['start_date'].replace('Z', '+00:00'))
    
    # Calculate end time based on elapsed_time (in seconds)
    run_end = run_start + timedelta(seconds=run['elapsed_time'])
    
    matched_tracks = []
    
    for item in recently_played_tracks:
        # Spotify's played_at is the time the track FINISHED playing
        track_played_at = datetime.fromisoformat(item['played_at'].replace('Z', '+00:00'))
        track_duration_ms = item['track']['duration_ms']
        
        # Estimate when the track started playing
        track_started_at = track_played_at - timedelta(milliseconds=track_duration_ms)
        
        # Check if the track overlaps with the run boundaries
        # overlapping means: track started before run ended AND track ended after run started
        if track_started_at <= run_end and track_played_at >= run_start:
            matched_tracks.append({
                "name": item['track']['name'],
                "artist": ", ".join([artist['name'] for artist in item['track']['artists']]),
                "album": item['track']['album']['name'],
                "album_image_url": item['track']['album']['images'][0]['url'] if item['track']['album']['images'] else None,
                "duration_ms": track_duration_ms,
                "played_at": item['played_at'],
                "external_url": item['track']['external_urls']['spotify']
            })
            
    # Optional: return sorted by when they were played (earliest first)
    matched_tracks.sort(key=lambda x: x['played_at'])
    return matched_tracks
