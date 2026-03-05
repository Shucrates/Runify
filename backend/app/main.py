from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api import auth, runs
import app.models.run  # Import to ensure metadata creates the tables

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Runify API")

# Configure CORS for our React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(runs.router, prefix="/runs", tags=["runs"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Runify API!"}
