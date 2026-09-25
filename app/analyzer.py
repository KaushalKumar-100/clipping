import json, os
from openai import OpenAI

SYSTEM="""You are a professional short-form video editor and content strategist.
Select 5 or 6 genuinely strong standalone Shorts/Reels/TikTok sections from a timestamped YouTube transcript.
Do not divide the video evenly. Never invent dialogue, events, timestamps, or facts absent from the transcript.
Prefer strong hooks, curiosity, mini-stories, surprising facts, useful insights, emotional/entertaining moments and satisfying payoffs.
Avoid intros, greetings, sponsors, filler, repetition, dead air, context-dependent fragments and abrupt endings.
Rank strongest to weakest. Timestamps must be supported by the supplied transcript.
For each clip, explain hook, retention, payoff, standalone value and shareability.
Return strict JSON only."""

SCHEMA={"type":"object","properties":{"shorts":{"type":"array","minItems":5,"maxItems":6,"items":{
"type":"object","properties":{
"rank":{"type":"integer"},"start":{"type":"number"},"end":{"type":"number"},
"hook":{"type":"string"},"why":{"type":"string"},"title":{"type":"string"},
"headline":{"type":"string"},"editing":{"type":"array","items":{"type":"string"}},
"trim":{"type":"string"},"retention":{"type":"string"}},
"required":["rank","start","end","hook","why","title","headline","editing","trim","retention"],
"additionalProperties":False}}},"required":["shorts"],"additionalProperties":False}

def analyze_clips(video):
    key=os.getenv("OPENAI_API_KEY")
    if not key: raise ValueError("OPENAI_API_KEY is required. Add it to .env.")
    transcript="\n".join(f'[{c["start"]:.2f}-{c["end"]:.2f}] {c["text"]}' for c in video["captions"])
    client=OpenAI(api_key=key)
    prompt=f"""VIDEO TITLE: {video["title"]}
VIDEO DURATION: {video["duration"]} seconds

TIMESTAMPED TRANSCRIPT:
{transcript}

Return the strongest 5–6 standalone short-form sections. Use exact numeric seconds.
Target roughly 20–90 seconds, but preserve a natural complete thought when necessary.
Editing should assume 9:16 vertical video."""
    r=client.responses.create(model=os.getenv("OPENAI_MODEL","gpt-5-mini"),
        instructions=SYSTEM,input=prompt,
        text={"format":{"type":"json_schema","name":"clip_analysis","schema":SCHEMA,"strict":True}})
    data=json.loads(r.output_text)
    duration=float(video["duration"])
    for s in data["shorts"]:
        s["start"]=max(0,min(float(s["start"]),duration))
        s["end"]=max(s["start"],min(float(s["end"]),duration))
        s["duration"]=round(s["end"]-s["start"],2)
    data["shorts"]=sorted(data["shorts"],key=lambda x:x["rank"])
    return {"video_title":video["title"],"approx_duration":video["duration"],
            "main_topic":video["title"],"number_of_shorts":len(data["shorts"]),
            "shorts":data["shorts"]}
