import os
from groq import AsyncGroq
from app.core.config import settings
import asyncio


def _build_prompt(run: dict, tracks: list[dict]) -> str:
    """Build a rich, descriptive prompt for the AI from run data and track list."""
    distance_km = run["distance_meters"] / 1000
    total_minutes = run["elapsed_time_seconds"] / 60
    pace_min_per_km = total_minutes / distance_km if distance_km > 0 else 0
    pace_str = f"{int(pace_min_per_km)}:{int((pace_min_per_km % 1) * 60):02d} min/km"

    if tracks:
        track_lines = "\n".join(
            [f"  {i+1}. \"{t['name']}\" by {t['artist']}" for i, t in enumerate(tracks)]
        )
    else:
        track_lines = "  No tracks recorded."

    prompt = f"""You are Runify AI — an enthusiastic, insightful running coach and sports psychologist who loves music.

A runner just completed a run. Based on the run stats and the music they listened to, generate a vivid, personalised AI Run Report.

--- RUN DATA ---
Run Name: {run["name"]}
Date: {run["start_date"]}
Distance: {distance_km:.2f} km
Time: {int(total_minutes)} minutes {int((total_minutes % 1) * 60)} seconds
Pace: {pace_str}

--- TRACKS LISTENED TO ---
{track_lines}

--- YOUR TASK ---
Write a structured run report with EXACTLY these 4 sections using markdown headers:

## 🏃 Run Summary
A 2-3 sentence vivid narrative describing the run — talk about the effort level, what {distance_km:.1f} km in {int(total_minutes)} minutes means for a runner, and whether the pace was easy, moderate, or hard.

## 🎵 Vibe & Mood Analysis
Analyse the music playlist. What does the genre/artist mix say about the runner's mood and energy going in? What was the overall sonic vibe — pump-up, chill, melancholic, aggressive? How did the music likely influence the run?

## 💡 What Went Well
2-3 bullet points highlighting positives — great pace, solid endurance, good distance, or how the music choice supported the effort.

## 🚀 How To Improve
2-3 actionable, specific tips to make the NEXT run even better — pacing strategies, music tempo adjustments, distance goals, or training suggestions based on this session.

Keep the tone energetic, motivating, and personal. Do NOT use filler phrases like "Great job!" — be specific and insightful.
"""
    return prompt


async def generate_run_summary(run: dict, tracks: list[dict]) -> str:
    """
    Call Groq API using the async client. 
    Note: We changed it to async since Groq has an async client, and FastAPI handles async well.
    But since the original was sync, wait, `ai.py` calls this sync or async? Let's check `ai.py`... 
    We will just make it standard synchronous to avoid breaking `ai.py` if it relies on blocking mode.
    """
    pass

import groq

def generate_run_summary(run: dict, tracks: list[dict]) -> str:
    """
    Call Groq API using the sync client.
    """
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing in the environment.")
    
    prompt = _build_prompt(run, tracks)
    
    client = groq.Groq(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            # llama3-70b-8192 or llama3-8b-8192 or mixtral-8x7b-32768
            model="llama-3.1-8b-instant",
            temperature=0.8,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Groq API failed. Last error: {str(e)}")
