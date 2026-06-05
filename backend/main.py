import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel

# Load .env from project root (priority) or backend/ directory
_root = Path(__file__).resolve().parent.parent
_dotenv_path = _root / ".env"
if _dotenv_path.exists():
    load_dotenv(_dotenv_path)
else:
    load_dotenv(Path(__file__).resolve().parent / ".env")

app = FastAPI(title="Novel2ScriptAl API")

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


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/convert", response_model=ConvertResponse)
def convert(payload: ConvertRequest):
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

    return ConvertResponse(yaml=yaml_str)


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
# Serve built frontend in production (after all API routes)
# ---------------------------------------------------------------------------
_frontend_dist = (_root / "frontend" / "dist").resolve()
if _frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="frontend")
