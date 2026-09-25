import re
import tempfile
from pathlib import Path
from yt_dlp import YoutubeDL

def parse_vtt(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    blocks = re.split(r"\n\s*\n", text)
    items = []
    for block in blocks:
        lines = [x.strip() for x in block.splitlines() if x.strip()]
        timing = next((x for x in lines if "-->" in x), None)
        if not timing:
            continue
        try:
            a, b = [x.strip().split()[0] for x in timing.split("-->")]
            def sec(v):
                v = v.replace(",", ".")
                p = v.split(":")
                if len(p) == 3: return int(p[0])*3600 + int(p[1])*60 + float(p[2])
                return int(p[0])*60 + float(p[1])
            i = lines.index(timing)
            caption = re.sub(r"<[^>]+>", "", " ".join(lines[i+1:]))
            caption = re.sub(r"\s+", " ", caption).strip()
            if caption: items.append({"start":sec(a),"end":sec(b),"text":caption})
        except Exception:
            pass
    out=[]
    for x in items:
        if not out or x["text"] != out[-1]["text"]: out.append(x)
    return out

def get_video_transcript(url: str):
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/"video"
        opts={
            "quiet":True,"no_warnings":True,"skip_download":True,
            "writesubtitles":True,"writeautomaticsub":True,
            "subtitleslangs":["en","en-US","en-GB"],"subtitlesformat":"vtt",
            "outtmpl":str(out)
        }
        with YoutubeDL(opts) as ydl:
            info=ydl.extract_info(url, download=False)
            if not info.get("subtitles") and not info.get("automatic_captions"):
                raise ValueError("This video does not expose accessible captions.")
            ydl.download([url])
        files=list(Path(td).glob("*.vtt"))
        if not files: raise ValueError("Captions were detected but could not be downloaded.")
        captions=parse_vtt(files[0])
        if not captions: raise ValueError("The downloaded captions were empty or unreadable.")
        return {"title":info.get("title") or "Untitled","duration":info.get("duration") or 0,
                "url":url,"captions":captions}
