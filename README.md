# ClipForge

YouTube Short-form Clip Analyzer.

Paste a public YouTube URL and ClipForge:
- fetches accessible captions with yt-dlp
- preserves caption timestamps
- selects 5–6 strongest standalone moments with an LLM
- returns exact start/end, hook, title, headline, editing instructions, trimming notes and retention analysis
- never intentionally invents timestamps or dialogue

## Local setup

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload

Open http://127.0.0.1:8000

Set OPENAI_API_KEY in .env.

## Deployment
A Render blueprint is included in render.yaml.

## Important
The analyzer requires a public YouTube video with accessible captions. If captions cannot be retrieved, it returns an actionable error instead of guessing.
