# Novel2ScriptAl — AI 小说转剧本工具

基于 **DeepSeek 大模型**的全栈 AI 编剧助手。用户粘贴或导入小说文本，选择改编风格，AI 自动生成符合行业标准的 YAML 格式剧本。支持 6 大类 18 种子风格、角色一致性校验、剧本编辑导出、文件夹管理等全链路功能。

### 📺 演示视频

> **点击下方链接查看完整功能演示：**
>
> 🔗 **[演示视频 — Bilibili](https://www.bilibili.com/video/BV19VEp6qEfv/)**

---

## 功能概述

| 模块 | 功能 |
|------|------|
|  **AI 剧本生成** | 调用 DeepSeek 将小说转 YAML 剧本，含元数据、角色表、场景列表 |
|  **6 大类 18 风格** | 写实、商业、文艺、奇幻、悬疑、喜剧，每类 3 种子风格 |
|  **章节识别** | 自动检测"第X章"标记，为每个 scene 添加 chapter_index/title |
|  **情感标签** | 可选 mood / suggested_lighting / suggested_sound 三字段 |
|  **角色一致性校验** | DeepSeek 分析角色特征，检查对话是否符合人设 |
|  **多格式导出** | YAML / 人读 TXT / Final Draft FDX（可导入专业编剧软件） |
|  **文件夹管理** | 创建、重命名文件夹，将剧本分类保存 |
|  **历史记录** | 按时间倒序展示，支持分页 |
|  **剧本编辑** | 左右双栏实时编辑原文和 YAML，支持保存 |
|  **单句情感定义** | 选中台词或动作描述，单独设置该场景的情绪标签 |
|  **四套主题** | 暗夜魔典 / 羊皮卷 / 浪漫影棚 / 冷静职场，localStorage 记忆 |
|  **Word 导入** | 前端解析 .docx 文件，直接提取文本 |
|  **用户认证** | 注册/登录，JWT token，路由守卫 |

---

## 技术栈与第三方依赖

### 前端

| 依赖 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| **[Vue 3](https://vuejs.org/)** | ^3.5.13 | 渐进式 JavaScript 框架，Composition API | MIT |
| **[Vite](https://vitejs.dev/)** | ^6.0.5 | 前端构建工具，HMR 热更新 | MIT |
| **[Pinia](https://pinia.vuejs.org/)** | ^2.3.0 | Vue 3 官方状态管理库 | MIT |
| **[Vue Router](https://router.vuejs.org/)** | ^4.5.0 | Vue 官方路由，支持 History 模式 + 导航守卫 | MIT |
| **[Axios](https://axios-http.com/)** | ^1.7.9 | HTTP 客户端，拦截器自动附加 JWT | MIT |
| **[mammoth.js](https://github.com/mwilliamson/mammoth.js)** | ^1.12.0 | 浏览器端解析 Word .docx 文件提取纯文本 | BSD-2 |
| **[@vitejs/plugin-vue](https://github.com/vitejs/vite-plugin-vue)** | ^5.2.1 | Vite 的 Vue 单文件组件编译插件 | MIT |

### 后端

| 依赖 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| **[FastAPI](https://fastapi.tiangolo.com/)** | 0.115.6 | 高性能 Python Web 框架，自动生成 OpenAPI 文档 | MIT |
| **[Uvicorn](https://www.uvicorn.org/)** | 0.34.0 | ASGI 服务器，支持热重载 | BSD-3 |
| **[OpenAI Python SDK](https://github.com/openai/openai-python)** | 1.58.1 | 调用 DeepSeek API（OpenAI 兼容接口） | Apache-2.0 |
| **[PyYAML](https://pyyaml.org/)** | 6.0.2 | YAML 解析与生成，用于剧本数据校验 | MIT |
| **[python-dotenv](https://github.com/theskumar/python-dotenv)** | 1.0.1 | 从 .env 文件加载环境变量（API Key） | BSD-3 |
| **[SQLAlchemy](https://www.sqlalchemy.org/)** | 2.0.36 | Python ORM，管理 SQLite 数据库 | MIT |
| **[passlib](https://passlib.readthedocs.io/)** | 1.7.4 | 密码哈希库，bcrypt 算法 | BSD-3 |
| **[bcrypt](https://github.com/pyca/bcrypt/)** | 4.0.1 | 密码哈希底层实现 | Apache-2.0 |
| **[python-jose](https://python-jose.readthedocs.io/)** | 3.3.0 | JWT 令牌签发与验证，HS256 算法 | MIT |

### 根项目

| 依赖 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| **[concurrently](https://github.com/open-cli-tools/concurrently)** | ^9.1.2 | 一键同时启动前后端开发服务器 | MIT |

### 第三方服务

| 服务 | 用途 |
|------|------|
| **[DeepSeek API](https://platform.deepseek.com/)** | 大语言模型，`deepseek-chat` 模型，OpenAI 兼容接口 |
| **SQLite** | 内嵌数据库，零配置，文件存储（`backend/data.db`） |

---

## 目录结构

```
Novel2ScriptAl/
├── backend/                    # 后端
│   ├── main.py                 # FastAPI 应用，API 路由，Prompt 模板
│   ├── models.py               # SQLAlchemy 数据模型 (User/Folder/ConversionRecord)
│   ├── database.py             # 数据库引擎 + Session
│   ├── auth.py                 # JWT 签发/验证 + bcrypt + get_current_user 依赖
│   └── requirements.txt        # Python 依赖
├── frontend/                   # 前端
│   ├── src/
│   │   ├── App.vue             # 根组件（主题系统、路由动画、全局 CSS 变量）
│   │   ├── main.js             # Vue 入口（挂载 Pinia + Router）
│   │   ├── api/index.js        # Axios 实例（JWT 拦截器）
│   │   ├── router/index.js     # Vue Router（路由守卫）
│   │   ├── stores/             # Pinia 状态管理
│   │   │   ├── auth.js         # 用户认证
│   │   │   ├── novel.js        # 小说内容 + 转换
│   │   │   ├── history.js      # 历史记录
│   │   │   ├── folder.js       # 文件夹管理
│   │   │   └── theme.js        # 四套主题
│   │   ├── views/              # 页面组件
│   │   │   ├── Home.vue        # 首页（双栏：输入 + YAML 输出）
│   │   │   ├── Login.vue       # 登录/注册
│   │   │   ├── History.vue     # 历史记录列表
│   │   │   ├── ScriptDetail.vue # 剧本详情（编辑/导出/校验）
│   │   │   └── FolderView.vue  # 文件夹管理
│   │   └── utils/export.js     # YAML → TXT / FDX 格式转换 + Blob 下载
│   ├── index.html              # HTML 入口
│   ├── vite.config.js          # Vite 配置（API 代理）
│   └── package.json            # 前端依赖
├── .env.example                # API Key 配置模板
├── .gitignore
├── package.json                # 根项目脚本（concurrently 一键启动）
└── README.md
```

---

## 快速启动

### 环境要求

- **Python** 3.10+
- **Node.js** 18+
- **DeepSeek API Key** ([获取](https://platform.deepseek.com/api_keys))

### 1. 配置 API Key

```bash
# 在项目根目录创建 .env 文件（参考 .env.example）
echo OPENAI_API_KEY=sk-xxxxxxxx > .env
```

### 2. 数据库准备

无需手动建库。首次启动时 SQLAlchemy 自动创建 SQLite 数据库文件 `backend/data.db`，包含：

- `users` — 用户表
- `folders` — 文件夹表
- `conversion_records` — 剧本记录表

### 3. 后端启动

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

启动后 FastAPI 会自动：
- 创建数据库表
- 为首次访问的用户创建「未归档」默认文件夹

### 4. 前端启动

**开发模式**（Vite HMR 热更新）：

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173（Vite 自动代理 /api → localhost:8000）
```

**生产模式**（单端口部署）：

```bash
cd frontend && npm run build   # 构建到 dist/
cd ../backend && uvicorn main:app --port 8000
# → http://localhost:8000（后端同时托管前端静态文件）
```

**一键启动**（开发双服务器）：

```bash
npm install   # 安装 concurrently
npm run dev   # 同时启动前端 :5173 + 后端 :8000
```

### 默认访问地址

| 模式 | URL |
|------|-----|
| 生产部署 | **http://localhost:8000** |
| 开发前端 | http://localhost:5173 |
| API 文档 | http://localhost:8000/docs |

---

## API 路由总览

### 公开

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/ping` | 健康检查 |
| POST | `/api/register` | 注册 |
| POST | `/api/login` | 登录 → JWT |

### 需认证（`Authorization: Bearer <token>`）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/me` | 当前用户信息 |
| POST | `/api/convert` | 小说转剧本（核心） |
| GET | `/api/history` | 历史记录列表（分页） |
| GET | `/api/history/{id}` | 历史记录详情 |
| PATCH | `/api/record/{id}/mood` | 更新场景 mood |
| PATCH | `/api/records/{id}` | 更新记录（原文+YAML） |
| POST | `/api/character_check` | 角色一致性校验 |
| GET | `/api/folders` | 文件夹列表 |
| POST | `/api/folders` | 创建文件夹 |
| PUT | `/api/folders/{id}` | 重命名文件夹 |
| GET | `/api/folders/{id}/records` | 文件夹下剧本 |
| PUT | `/api/records/{id}/folder` | 移动到文件夹 |

---

## 架构设计

```
┌───────────────────────────────────────────────┐
│                    Browser                     │
│  Vue 3 + Pinia + Router + CSS Variables       │
│  ┌─────────┐ ┌──────┐ ┌──────┐ ┌───────────┐ │
│  │ Home.vue │ │Login │ │History│ │FolderView │ │
│  └────┬─────┘ └──┬───┘ └──┬───┘ └─────┬─────┘ │
│       │           │        │           │        │
│       └───────────┴──── Axios ─────────┘        │
│              /api/*   (JWT Header)              │
└──────────────────────┬──────────────────────────┘
                       │
              ┌────────▼────────┐
              │    FastAPI       │
              │  CORS Middleware │
              │  StaticFiles     │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐  ┌──────▼──────┐  ┌───▼────┐
   │ Auth    │  │ /api/convert│  │ Folder │
   │ JWT     │  │ 6大类18风格 │  │ CRUD   │
   │ bcrypt  │  │ Prompt 构建 │  │ 移动   │
   └─────────┘  └──────┬──────┘  └────────┘
                       │
              ┌────────▼────────┐
              │   DeepSeek API   │
              │  (deepseek-chat) │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  YAML 校验/提取  │
              │  自动保存 DB     │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │    SQLite        │
              │  users/folders/  │
              │  conversion_records│
              └─────────────────┘
```

### 核心数据流

1. **认证流**：`POST /api/register` → bcrypt 哈希 → `POST /api/login` → JWT → `Authorization` Header
2. **转换流**：小说文本 → Prompt 构建 → DeepSeek → YAML 提取 → 解析校验 → 存库 + 返回
3. **主题流**：`theme.js` → CSS Variables → `document.documentElement.style.setProperty` → 全页面响应

---

## 测试

### 后端 API 测试

```bash
# 注册
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'

# 登录并获取 token
TOKEN=$(curl -s -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}' \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# 转换
curl -X POST http://localhost:8000/api/convert \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"novel_text":"第一章 相遇\n\n李明走进咖啡厅，看到了王芳。","style":"faithful_realism"}'

# 查看历史
curl http://localhost:8000/api/history -H "Authorization: Bearer $TOKEN"

# 角色校验
curl -X POST http://localhost:8000/api/character_check \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"record_id":1}'
```

### 前端手动测试

| 测试点 | 操作 | 预期 |
|--------|------|------|
| 注册/登录 | 访问 / → 跳转 /login → 注册 → 登录 | 进入首页 |
| 风格切换 | 选择大类 → 子风格联动 | 18 风格可选 |
| Word 导入 | 点击导入 → 选 .docx | 文本填入输入框 |
| 转换 | 粘贴文本 → 点转换 | YAML 含元数据+角色+场景 |
| 情感定义 | 选中台词 → 浮动按钮 → 改 mood | YAML 即时更新 |
| 导出 | 导出 ▾ → 三个格式 | 下载对应文件 |
| 主题切换 | 右上角选主题 | 全页面即时变色 |
| 文件夹 | 进入文件夹 → 新建 → 保存 | 剧本归档成功 |
| 角色校验 | 详情页点校验 | 弹出特征表+偏差报告 |
