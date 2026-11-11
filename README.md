# 我的智能体工作台（Agent Workbench）

一个全栈 AI 智能体工作台：基于 **Vue 3 + Flask + LangChain/LangGraph** 二次开发，支持多模型接入、内置工具调用、可视化工作流编排，以及基于 Playwright 的 RPA 浏览器自动化工具。

> 本项目基于开源项目 [openagent](https://github.com/Haohao-end/openagent) 进行二次开发与定制，上游许可见仓库根目录 `LICENSE`。

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Vue 3.4、Vite、Arco Design Vue、Pinia、Vue Router、Tailwind CSS、socket.io-client、ECharts、Vue Flow |
| 后端 | Flask 3.1、Flask-SQLAlchemy、Flask-Migrate、Celery、Flask-SocketIO、Authlib |
| Agent | LangChain 1.2、LangGraph 1.1 |
| 存储 | PostgreSQL 15、Redis 7（Weaviate 向量库预留） |
| 外部服务 | OpenAI 兼容协议大模型 API（火山方舟 / DeepSeek / 通义千问等） |

## 系统架构

```
前端层  Vue 3 工作台（对话、模型管理、插件、工作流画布）
          │  HTTP / REST、WebSocket
后端层  Flask API
          ├─ Agent 编排：LangGraph 状态图 + 工作流节点
          ├─ 内置工具系统：Token 统计 / Prompt 优化 / 历史压缩 / RPA 浏览器
          └─ 动态模型管理：自定义模型提供商 CRUD
          │  ORM
存储层  PostgreSQL（用户、会话、模型配置、工作流） + Redis（缓存 / 会话）
          │
外部层  大模型 API、OAuth 登录、RPA 浏览器（Playwright + Edge）
```

## 我负责 / 定制的模块

### 1. 动态模型管理
- 新增 `custom_model_provider` 数据表（模型名、Base URL、API Key、模型列表、能力特性、上下文窗口等，模型列表与特性用 JSONB 存储）。
- 提供后端 CRUD 接口与前端模型管理页；用户在界面添加 OpenAI 兼容模型即可调用，**无需修改 `.env` 或重启服务**。
- 模型保存前做连通性测试，配置错误可提前发现。

### 2. 内置工具系统
基于工具实体（`BuiltinProviderEntity` / `BuiltinToolEntity`）注册并接入助手运行时，自研三个工具：
- `token_counter`：统计对话 / 请求的 Token 用量；
- `prompt_optimizer`：对 Prompt 给出优化建议；
- `history_compressor`：压缩长对话历史，控制上下文长度。

### 3. RPA 浏览器自动化工具
- `providers/rpa_browser`：基于 Playwright 复用系统 Edge 浏览器，实现「打开网站 → 点击元素 → 输入文本」等操作工具。
- 配套 BOSS 直聘自动投递工作流（工作流模型 + 初始化脚本），把浏览器操作节点串成可执行流程。

### 4. 账号与会话
- 邮箱验证码登录、手机号验证码登录（开发模式验证码打印到控制台）；保留上游 GitHub / Google OAuth 登录。
- 会话自动命名、建议问题生成、最近对话列表实时刷新等会话体验优化。

### 5. 前端工作台
工作台首页、模型管理页、插件页（内置 / 自定义两个 Tab）、侧边栏会话列表与时间显示、启动动画、桌宠悬浮组件、主题切换。

## Agent 实现要点

- **任务编排**：用 LangGraph 状态图组织 Agent 流程；工作流画布支持 LLM、工具调用、检索、HTTP 请求、分支等节点。
- **上下文管理**：通过历史压缩工具对长对话做摘要压缩，优先保留最近与相关内容，避免上下文超限。
- **工具调用**：模型根据意图选择工具并填写参数 → 后端执行工具 → 结果回传模型 → 模型结合结果继续生成或再次调用工具。
- **稳健性**：工具与模型调用加 try-catch 与降级处理；模型配置保存前测试连通性；异常给用户明确提示，不把错误直接抛出。

## 目录结构

```
openagent/
├── api/                     # Flask 后端
│   ├── app/http/            # 应用入口
│   ├── internal/
│   │   ├── core/            # agent / language_model / tools / workflow / memory / retrievers / vector_store
│   │   ├── model/           # SQLAlchemy 数据模型
│   │   ├── service/         # 业务逻辑
│   │   ├── handler/ router/ schema/ migration/ task/ schedule/
│   └── scripts/             # 工具与初始化脚本
├── ui/                      # Vue 3 前端
│   └── src/                 # views / components / stores / services / router / ...
├── docker/
└── docs/
```

## 本地运行

前置环境：Python 3.11+、Node 18+、PostgreSQL 15、Redis 7。

**后端**

```bash
cd api
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # 填写数据库、Redis、模型等配置
flask db upgrade             # 初始化 / 升级数据库表
FLASK_APP=app.http.app flask run --port=5001
```

**前端**

```bash
cd ui
npm install
npm run serve                # 默认 http://localhost:5173
```

服务端口：前端 5173、后端 5001、PostgreSQL 5432、Redis 6379。

## 安全与配置说明

- 所有密钥、数据库密码、模型 API Key 均通过 `.env` 或界面模型配置管理，**不写入代码仓库**；仓库内仅提供 `.env.example` 占位模板。
- 模型接入走 OpenAI 兼容协议；多模型配置保存在数据库中。

## 致谢与许可

- 上游基础框架：[Haohao-end/openagent](https://github.com/Haohao-end/openagent)。
- 本仓库在其基础上完成上述定制开发；开源许可以根目录 `LICENSE` 文件为准。
