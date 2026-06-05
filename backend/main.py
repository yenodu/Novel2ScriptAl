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
# Style definitions — 6 categories, 18 sub-styles
# ---------------------------------------------------------------------------
STYLE_CATEGORIES = {
    "realism": "写实生活化改编",
    "commercial": "商业化强戏剧改编",
    "arthouse": "文艺诗意化改编",
    "fantasy": "奇幻架空类改编",
    "suspense": "悬疑惊悚改编",
    "comedy": "喜剧夸张改编",
}

# Each sub-style: (category_key, label, system_prompt_addendum)
STYLE_MAP: dict[str, tuple[str, str, str]] = {
    # ---- 一、写实生活化改编 ----
    "faithful_realism": ("realism", "原著忠实写实",
        "改编风格：原著忠实写实。台词、情节、人物基本照搬原著，仅精简冗余心理描写，保留原著细节与氛围，"
        "适合文艺片、家庭剧。YAML 中 dialogue 尽量直接引用或略加润色原著对白。"),
    "slice_of_life": ("realism", "市井烟火写实",
        "改编风格：市井烟火写实。强化生活细节、方言口语、小人物琐碎日常，删减原著空想或夸张桥段，"
        "适配都市现实剧。YAML 中 action 需细致描写环境氛围和人物微表情，dialogue 可加入符合人设的口语化台词。"),
    "documentary": ("realism", "纪实改编",
        "改编风格：纪实改编。偏向纪录片式剧本，压缩戏剧冲突，保留原著真实事件脉络，人物行为贴合现实规律。"
        "YAML 中 heading 使用冷静客观的场景描述，action 以客观镜头语言为主。"),

    # ---- 二、商业化强戏剧改编 ----
    "fast_paced": ("commercial", "强爽点浓缩改编",
        "改编风格：强爽点浓缩改编。剔除原著慢节奏铺垫，密集冲突、升级线、反转，网文改短剧最常用。"
        "YAML 中每个 scene 需简短有力，heading 使用节奏感强的标题，dialogues 精简有力，scene 数量不宜过多。"),
    "family_friendly": ("commercial", "合家欢通俗改编",
        "改编风格：合家欢通俗改编。弱化原著阴暗、悲剧内容，优化人设使其更正面，可适当增加喜剧桥段，"
        "适配院线合家欢电影。YAML 整体基调轻快温暖。"),
    "crime_thriller": ("commercial", "悬疑刑侦商业化",
        "改编风格：悬疑刑侦商业化。从原著零散线索提炼主线，可加连环案件、正邪博弈、倒计时元素，"
        "适合悬疑小说改剧。YAML 中 scenes 需包含悬念节点，action 中可加入暗示线索的细节。"),

    # ---- 三、文艺诗意化改编 ----
    "poetic_minimalist": ("arthouse", "意象留白改编",
        "改编风格：意象留白改编。舍弃大段叙事，把原著心理描写、环境描写转化为镜头画面和视觉意象，"
        "大量留白，弱化直白台词，适合院线文艺片。YAML 中 action 侧重画面感和情绪氛围，dialogues 极度精简。"),
    "lyrical_prose": ("arthouse", "抒情散文诗改编",
        "改编风格：抒情散文诗改编。拆分原著线性剧情，穿插回忆、幻想片段，侧重情绪表达而非情节推进。"
        "YAML 中可加入「闪回」「梦境」等特殊 scene heading，action 使用散文式语言。"),
    "absurdist_arthouse": ("arthouse", "荒诞文艺改编",
        "改编风格：荒诞文艺改编。放大原著讽刺、荒诞设定，弱化现实逻辑，适合先锋话剧、小众实验电影。"
        "YAML 中允许出现超现实 heading 和非线性 scene 结构，dialogues 可包含荒诞对白。"),

    # ---- 四、奇幻架空类改编 ----
    "epic_fantasy": ("fantasy", "史诗宏大改编",
        "改编风格：史诗宏大改编。扩充世界观、大场面战争/仙魔大战，精简支线配角但保留关键人物弧光，"
        "适合改编大部头奇幻名著。YAML 中 action 需包含对奇幻元素、宏大场景的详细描述。"),
    "light_fantasy": ("fantasy", "轻量化魔改改编",
        "改编风格：轻量化魔改改编。砍掉原著复杂修炼体系或世界观设定，简化背景，保留主角主线，"
        "做成快餐式网剧。YAML 结构简洁，每个 scene 快速推进剧情。"),
    "soft_scifi": ("fantasy", "软科幻落地改编",
        "改编风格：软科幻落地改编。把原著高概念科幻设定落地到生活化场景，减少晦涩理论，"
        "贴合普通人观感。YAML 中科幻设定通过 dialogue 和 action 自然呈现，不做大段解释。"),

    # ---- 五、悬疑惊悚改编 ----
    "honkaku_mystery": ("suspense", "本格推理改编",
        "改编风格：本格推理改编。严格沿用原著诡计、线索排布，忠于推理逻辑，适合侦探剧、悬疑电影。"
        "YAML 中 scenes 需按时间线或调查步骤有序推进，每个 scene 可包含「clue」提示。"),
    "horror_atmosphere": ("suspense", "惊悚氛围改编",
        "改编风格：惊悚氛围改编。弱化原著文字解谜部分，强化镜头恐怖氛围、音效提示、突然惊吓，"
        "适合恐怖小说改恐怖片。YAML 中 action 侧重环境阴暗描写和紧张感营造。"),
    "social_suspense": ("suspense", "社会派悬疑改编",
        "改编风格：社会派悬疑改编。以案件引出社会问题，扩充配角故事线和社会背景，"
        "适合国内刑侦悬疑剧。YAML 中除主线案件外可加入反映社会问题的支线 scene。"),

    # ---- 六、喜剧夸张改编 ----
    "slapstick_absurd": ("comedy", "无厘头魔改",
        "改编风格：无厘头魔改。在原著基础上加入大量原创搞笑桥段、错位台词、夸张人设，"
        "港式喜剧风格。YAML 中 dialogue 可加入无厘头对白和错位梗，action 可包含夸张的喜剧动作描写。"),
    "light_comedy": ("comedy", "轻喜剧落地改编",
        "改编风格：轻喜剧落地改编。保留原著幽默内核但贴合现实人设，删减离谱或过于夸张的设定，"
        "适合都市甜宠喜剧。YAML 中 dialogue 保持轻松幽默但不过度夸张，action 侧重温馨氛围。"),
    "satirical_dark": ("comedy", "讽刺黑色喜剧",
        "改编风格：讽刺黑色喜剧。放大原著讽刺内核，小人物倒霉、反套路剧情，"
        "适合黑色幽默院线剧本。YAML 中允许悲剧性结局和反套路设计，dialogue 可含冷嘲热讽。"),
}

ALL_STYLES = frozenset(STYLE_MAP.keys())

BASE_YAML_STRUCTURE = """YAML 结构示例：
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
```"""


MOOD_FIELDS = (
    "\n此外，每个 scene 必须额外包含以下三个字段：\n"
    "  - mood: 情绪标签（如\"紧张\"、\"浪漫\"、\"诡异\"、\"温馨\"）\n"
    "  - suggested_lighting: 建议灯光（如\"暖黄顶光\"、\"冷蓝侧光\"、\"自然光\"）\n"
    "  - suggested_sound: 建议音效/配乐（如\"雨声白噪\"、\"低沉弦乐\"、\"寂静\"）\n"
)


def build_system_prompt(style: str, add_mood: bool = False) -> str:
    _, label, addendum = STYLE_MAP[style]
    prompt = (
        f"你是一位专业编剧。用户会提供一段小说文本，你需要将其转换为 {label}。\n\n"
        f"{addendum}\n\n"
        f"YAML 必须包含：\n"
        f"1. title——从文本中提取或概括。\n"
        f"2. scenes 列表——每个 scene 含 scene_id（从1开始）、heading（场景标题）、"
        f"action（动作与环境描述）、dialogues（列表，每条含 character 和 line）。"
    )
    if add_mood:
        prompt += MOOD_FIELDS
    prompt += (
        f"\n3. 输出必须是纯 YAML，用 ```yaml 开头、``` 结尾的代码块包裹。\n"
        f"   代码块外不要有任何文字，代码块内不要插入评论。\n\n"
        f"{BASE_YAML_STRUCTURE}"
    )
    return prompt


def build_user_prompt(novel_text: str, style: str) -> str:
    _, label, _ = STYLE_MAP[style]
    return f"请将以下小说内容转换为「{label}」风格的 YAML 剧本：\n\n{novel_text}"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class ConvertRequest(BaseModel):
    novel_text: str
    style: str = "faithful_realism"
    add_mood: bool = False


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


class CharacterCheckRequest(BaseModel):
    record_id: int | None = None
    script_yaml: str | None = None
    features_override: dict[str, dict[str, str]] | None = None


class CharacterFeature(BaseModel):
    personality: str = ""
    catchphrase: str = ""
    appearance: str = ""


class Deviation(BaseModel):
    character: str
    line: str
    issue: str


class CharacterCheckResponse(BaseModel):
    extracted_features: dict[str, CharacterFeature]
    deviations: list[Deviation]


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
    if payload.style not in ALL_STYLES:
        raise HTTPException(
            status_code=422,
            detail=f"不支持的 style: '{payload.style}'",
        )

    client = get_client()
    system_prompt = build_system_prompt(payload.style, payload.add_mood)
    user_prompt = build_user_prompt(payload.novel_text, payload.style)

    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
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
# Character consistency check (protected)
# ---------------------------------------------------------------------------
CHARACTER_PROMPT = """你是一位专业的剧本审校。请完成以下两项任务并返回 JSON。

任务1：从小说文本中提取至少三个角色的特征。
对每个角色，提供：
  - personality: 性格描述（一句话）
  - catchphrase: 口头禅或说话风格（如原文没有则推断）
  - appearance: 外貌描述（如原文没有则写"未描述"）

任务2：检查剧本 YAML 中每个角色的对话是否与其特征一致。
对不一致的地方，指出：
  - character: 角色名
  - line: 具体台词
  - issue: 不一致的问题描述

返回必须是纯 JSON，用 ```json 代码块包裹。格式如下：
```json
{
  "extracted_features": {
    "角色名": { "personality": "...", "catchphrase": "...", "appearance": "..." }
  },
  "deviations": [
    { "character": "角色名", "line": "台词", "issue": "问题描述" }
  ]
}
```
"""


@app.post("/api/character_check", response_model=CharacterCheckResponse)
def character_check(
    payload: CharacterCheckRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Resolve novel_text + script_yaml from record_id or direct input
    if payload.record_id:
        record = db.query(ConversionRecord).filter_by(id=payload.record_id, user_id=user.id).first()
        if not record:
            raise HTTPException(status_code=404, detail="记录不存在")
        novel_text = record.novel_text
        script_yaml = record.script_yaml
    elif payload.script_yaml:
        novel_text = ""
        script_yaml = payload.script_yaml
    else:
        raise HTTPException(status_code=422, detail="请提供 record_id 或 script_yaml")

    client = get_client()

    # Build prompt
    override_note = ""
    if payload.features_override:
        override_note = f"\n注意：以下角色特征由用户手动指定，优先使用：{payload.features_override}\n"

    user_prompt = (
        f"小说原文：\n{novel_text}\n\n"
        f"剧本 YAML：\n{script_yaml}\n"
        f"{override_note}"
    )

    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": CHARACTER_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
            timeout=60,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"DeepSeek API 调用失败: {e}")

    raw = resp.choices[0].message.content or ""

    # Extract JSON from ```json ... ```
    import json
    try:
        json_str = _extract_json_block(raw)
        data = json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=502, detail=f"LLM 返回格式异常: {e}\n原始输出:\n{raw[:500]}")

    features = {
        name: CharacterFeature(
            personality=f.get("personality", ""),
            catchphrase=f.get("catchphrase", ""),
            appearance=f.get("appearance", ""),
        )
        for name, f in data.get("extracted_features", {}).items()
    }
    deviations = [
        Deviation(character=d["character"], line=d["line"], issue=d["issue"])
        for d in data.get("deviations", [])
    ]

    return CharacterCheckResponse(extracted_features=features, deviations=deviations)


def _extract_json_block(text: str) -> str:
    start = text.find("```json")
    if start == -1:
        start = text.find("```")
        if start == -1:
            return text.strip()
        start += 3
    else:
        start += 7
    end = text.find("```", start)
    if end == -1:
        return text[start:].strip()
    return text[start:end].strip()


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
