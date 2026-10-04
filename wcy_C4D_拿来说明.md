# C4D 拿来说明 —— 用了哪些库/工具、参考了什么

## 软件与工具

| 名称 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| Ollama | 0.35.1 | 本地大模型运行时（下载、加载、提供 OpenAI 兼容 API） | MIT |
| gemma4:e4b | Q4_K_M 量化 | 本地大模型本体（4.5B 有效参数） | Apache 2.0（Gemma 使用条款） |
| Homebrew | 7.0.7 | macOS 包管理器，用于安装 Ollama | BSD |
| Python | 3.13.12 | Agent 脚本运行环境 | PSF |
| WorkBuddy（CodeBuddy） | — | AI 编程助手：环境搭建、代码编写、文档撰写 | — |

## Python 库（pip 安装）

| 库 | 版本 | 用途 |
|----|------|------|
| requests | 2.34.2 | 向本地 Ollama 的 `http://localhost:11434/api/chat` 发 HTTP 请求 |
| folium | 0.20.0 | 生成交互式 Leaflet 地图 HTML（标记、弹窗、图层控制） |
| （folium 依赖）jinja2 / branca / numpy / xyzservices 等 | — | folium 自动安装的依赖 |

## 前端资源（folium 自动内嵌，未手写）

- Leaflet.js 1.9.x —— 地图交互引擎（缩放/拖动/点击）
- OpenStreetMap —— 地图底图瓦片（查看地图时需联网加载底图；模型推理本身完全离线）
- Font Awesome（folium.Icon 的 graduation-cap 图标）

## 参考资料与灵感来源

| 来源 | 参考了什么 |
|------|-----------|
| `CHALLENGE.md` / `C4D.pdf` | 挑战要求、Ollama 最简示例的结构（system 提示 + JSON 字段要求） |
| `C4D 补充说明.pdf` | 非 CS 专业简化通道说明；地图/Agent 为加分项的定位 |
| Ollama API 文档（ollama.com） | `/api/chat` 的 `format: "json"` 参数、`eval_count`/`eval_duration` 性能字段 |
| Folium 官方文档（python-visualization.github.io/folium） | Marker/Popup/LayerControl 用法 |
| 新郑市地理常识 | 坐标校验 bbox（34.30–34.60N, 113.60–113.90E）的设定依据 |

## 素材说明

- 全部代码由 AI 助手根据我的需求生成，我再逐行阅读中文注释理解，无抄袭模板
- 地点数据 100% 由本地 `gemma4:e4b` 模型生成（见 `wcy_C4D_output_logs/step2_locations_raw.json` 原始输出）
- 未使用任何云端大模型 API，未付费使用任何服务
