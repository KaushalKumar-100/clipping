import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv
from app.youtube import get_video_transcript
from app.analyzer import analyze_clips

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(title="ClipForge", version="1.0.0")

origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

class AnalyzeRequest(BaseModel):
    url: HttpUrl

@app.get("/api/health")
def health():
    return {"ok": True, "service": "clipforge"}

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    try:
        video = get_video_transcript(str(req.url))
        return analyze_clips(video)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

@app.get("/")
def index():
    return FileResponse(BASE_DIR / "web" / "index.html")
