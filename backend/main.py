from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Novel2ScriptAl API")

# CORS — allow frontend dev server origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConvertRequest(BaseModel):
    text: str


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/convert")
def convert(payload: ConvertRequest):
    """Stub — will be replaced with real script-generation logic."""
    char_count = len(payload.text)
    return {
        "input_chars": char_count,
        "script": f"[TODO] 剧本将从 {char_count} 字的小说中生成。",
    }
