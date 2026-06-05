import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, User, ConversionRecord
from auth import hash_password, verify_password, create_access_token, get_current_user

# Load .env from project root (priority) or backend/ directory
_root = Path(__file__).resolve().parent.parent
_dotenv_path = _root / ".env"
if _dotenv_path.exists():
    load_dotenv(_dotenv_path)
else:
    load_dotenv(Path(__file__).resolve().parent / ".env")

app = FastAPI(title="Novel2ScriptAl API")

# Create DB tables on startup
Base.metadata.create_all(bind=engine)

# CORS — allow frontend dev server origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# DeepSeek client (lazy init — only when API key is available)
# ---------------------------------------------------------------------------
_deepseek_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _deepseek_client
    if _deepseek_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="未配置 OPENAI_API_KEY。请在项目根目录创建 .env 文件，写入 OPENAI_API_KEY=sk-xxx",
            )
        _deepseek_client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
    return _deepseek_client


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------
STYLE_LABELS = {
    "film": "电影剧本 (film script) — 标准影视分镜，headings 使用场景/镜头格式",
    "stage": "舞台剧剧本 (stage play) — 分幕/分场，headings 使用舞台调度格式",
    "short": "短视频脚本 (short video) — 快节奏，单场景或简短短片格式",
}

SYSTEM_PROMPT = """你是一位专业编剧。用户会提供一段小说文本，你需要将其转换成一个结构化的 YAML 剧本。

要求：
1. 从文本中提取或概括一个合适的 title。
2. 将内容拆分为多个 scenes，每个 scene 包含：
   - scene_id: 序号（从 1 开始）
   - heading: 场景标题（格式如「内景 - 书房 - 日」或「外景 - 公园 - 黄昏」）
   - action: 该场景的动作与环境描述
   - dialogues: 对话列表，每条包含 character（说话角色）和 line（台词）

3. 输出必须是纯 YAML，用 ```yaml 代码块包裹。不要输出任何解释、注释或额外文字。

YAML 结构示例：
```yaml
title: 重逢
scenes:
  - scene_id: 1
    heading: 内景 - 咖啡厅 - 下午
    action: 阳光透过落地窗洒在木质地板上，李明推门走进咖啡厅。
    dialogues:
      - character: 李明
        line: 好久不见。
      - character: 王芳
        line: 是啊，三年了。
```
"""


def build_user_prompt(novel_text: str, style: str) -> str:
    style_desc = STYLE_LABELS.get(style, STYLE_LABELS["film"])
    return f"请将以下小说内容转换为 {style_desc}：\n\n{novel_text}"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class ConvertRequest(BaseModel):
    novel_text: str
    style: str = "film"  # film / stage / short


class ConvertResponse(BaseModel):
    yaml: str
    record_id: int | None = None


class AuthRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3 or len(v) > 32:
            raise ValueError("用户名长度应为 3-32 个字符")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("密码长度至少 6 个字符")
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class HistoryItem(BaseModel):
    id: int
    novel_preview: str
    style: str
    created_at: str


class HistoryDetail(BaseModel):
    id: int
    novel_text: str
    script_yaml: str
    style: str
    created_at: str


# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------
@app.get("/ping")
def ping():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Auth endpoints (public)
# ---------------------------------------------------------------------------
@app.post("/api/register", response_model=UserResponse)
def register(payload: AuthRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(username=payload.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="用户名已存在")

    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        username=user.username,
        created_at=user.created_at.isoformat(),
    )


@app.post("/api/login", response_model=TokenResponse)
def login(payload: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, username=user.username)


@app.get("/api/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Protected endpoints
# ---------------------------------------------------------------------------
@app.post("/api/convert", response_model=ConvertResponse)
def convert(
    payload: ConvertRequest,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.style not in ("film", "stage", "short"):
        raise HTTPException(
            status_code=422,
            detail=f"不支持的 style: '{payload.style}'，可选值为 film / stage / short",
        )

    client = get_client()
    user_prompt = build_user_prompt(payload.novel_text, payload.style)

    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=4096,
            timeout=60,
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"DeepSeek API 调用失败: {e}",
        )

    raw = resp.choices[0].message.content or ""

    # Extract YAML block from ```yaml ... ```
    yaml_str = _extract_yaml_block(raw)

    # Validate it's parseable YAML
    try:
        yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=502,
            detail=f"LLM 返回的不是有效 YAML。原始输出:\n{raw[:500]}",
        )

    # Auto-save record (failure must not break the response)
    record_id = None
    try:
        record = ConversionRecord(
            user_id=_user.id,
            novel_text=payload.novel_text,
            script_yaml=yaml_str,
            style=payload.style,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        record_id = record.id
    except Exception:
        logging.exception("Failed to save ConversionRecord")

    return ConvertResponse(yaml=yaml_str, record_id=record_id)


def _extract_yaml_block(text: str) -> str:
    """Extract the content between ```yaml and ``` markers."""
    # Look for ```yaml ... ``` block
    start = text.find("```yaml")
    if start == -1:
        start = text.find("```")
        if start == -1:
            return text.strip()
        # It's ``` without yaml marker
        start += 3
    else:
        start += 7  # len("```yaml")

    end = text.find("```", start)
    if end == -1:
        return text[start:].strip()

    return text[start:end].strip()


# ---------------------------------------------------------------------------
# History endpoints (protected)
# ---------------------------------------------------------------------------
@app.get("/api/history", response_model=list[HistoryItem])
def history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = (
        db.query(ConversionRecord)
        .filter_by(user_id=user.id)
        .order_by(ConversionRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        HistoryItem(
            id=r.id,
            novel_preview=r.novel_text[:100],
            style=r.style,
            created_at=r.created_at.isoformat(),
        )
        for r in records
    ]


@app.get("/api/history/{record_id}", response_model=HistoryDetail)
def history_detail(
    record_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(ConversionRecord).filter_by(id=record_id, user_id=user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return HistoryDetail(
        id=record.id,
        novel_text=record.novel_text,
        script_yaml=record.script_yaml,
        style=record.style,
        created_at=record.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# SPA fallback — serve built frontend for all unmatched GET requests
# Must be defined LAST so API routes take precedence.
# ---------------------------------------------------------------------------
_frontend_dist = (_root / "frontend" / "dist").resolve()
_frontend_index = _frontend_dist / "index.html"


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve static files; fall back to index.html for SPA client-side routes."""
    if not _frontend_dist.is_dir():
        raise HTTPException(status_code=404, detail="前端尚未构建，请先运行 npm run build")

    file_path = _frontend_dist / full_path
    if file_path.is_file():
        return FileResponse(file_path)

    # SPA fallback — /login, /, or any client-side route
    if _frontend_index.is_file():
        return FileResponse(_frontend_index)

    raise HTTPException(status_code=404, detail="Not Found")
