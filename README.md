# Runify 🏃‍♂️🎵

**Runify** is a full-stack web application that intelligently synchronizes your Strava running history with your Spotify listening history. It cross-references timestamps to show you exactly which tracks fueled your runs.

![Runify Prototype Concept](https://via.placeholder.com/800x400.png?text=Runify+Dashboard+Preview)

## Features
- **Dual OAuth Integration:** Securely connect both Strava and Spotify accounts.
- **Timestamp Matching:** Automatically calculates exactly when a track was playing based on track duration, Spotify `played_at` timestamps, and Strava activity boundaries.
- **Smart Syncing:** Prevent duplication by keeping track of which runs have already been matched and saved to the local database.
- **Beautiful Dashboard:** Clean, dark-themed UI built with React and Tailwind CSS v4.

## Tech Stack
**Frontend:**
- [React 19](https://react.dev/) + [Vite](https://vitejs.dev/)
- [Tailwind CSS v4](https://tailwindcss.com/)
- [React Router v7](https://reactrouter.com/)
- Axios & Lucide React Icons

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) (Python)
- [SQLAlchemy](https://www.sqlalchemy.org/) (SQLite)
- Uvicorn & HTTPX

---

## 🚀 Local Setup Instructions

### Prerequisites
- Node.js (v20+)
- Python (v3.10+)
- Developer credentials from [Strava](https://developers.strava.com/) and [Spotify](https://developer.spotify.com/dashboard)

### 1. Backend Setup
Navigate to the `backend` directory, set up your Python virtual environment, and install dependencies.
```bash
cd backend
python -m venv venv
# On Windows: .\venv\Scripts\Activate.ps1
# On Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory using your API credentials:
```env
STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
DATABASE_URL=sqlite:///./runify.db
```

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
*(The backend runs on `http://127.0.0.1:8000`)*

---

### 2. Frontend Setup
Open a new terminal, navigate to the `frontend` directory, and install the Node dependencies.
```bash
cd frontend
npm install
```

Start the Vite development server:
```bash
npm run dev
```
*(The frontend runs on `http://localhost:5173`)*

---

### 3. Important API Callback Configurations
To prevent security errors during the OAuth flow, ensure you have registered the correct redirect URIs in both developer dashboards:

- **Strava API Settings**: Set Authorization Callback Domain to `localhost`
- **Spotify API Settings**: Add Redirect URI `http://127.0.0.1:8000/auth/spotify/callback`

---

## Future Roadmap (Next Steps)
- Automatically generate a Spotify Playlist for the user containing the matched tracks.
- Webhook integration with Strava to automatically sync when a run is finished (avoiding the Spotify 50-track history limit).
- Map visualization of the run path using Strava polyline data.