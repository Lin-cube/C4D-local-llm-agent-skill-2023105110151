# C4D 本地大模型 Agent 技能 · 挑战作业提交

- 挑战：C4D 本地大模型 Agent 技能
- 学生学号：2023105110151（WangChunYan，计算机通道）
- 路线：本地大模型部署 → 具备记忆与技能的 Agent → 函数调用生成地点数据 → Folium 交互地图 → 截图/录屏佐证

## 交付物清单

| 交付物 | 文件 |
| --- | --- |
| Agent 技能 | `wcy_C4D_agent-skill/`（Level 1 对话 + Level 2 Agent 地图，含 pyproject / uv.lock / README） |
| Demo | `wcy_C4D_map.html`（交互地图） |
| AI 使用日志 | `wcy_C4D_AI日志.md` |
| AAR 复盘 | `wcy_C4D_AAR.md` |
| 运行证据 | `wcy_C4D_output_screenshots/`（设备 / 本地模型调用 / 地图 3 张截图 + 录屏） |

## 过程与佐证文档

- `wcy_C4D_方案设计.md`、`wcy_C4D_教学说明.md`、`wcy_C4D_验证报告.md`、`wcy_C4D_拿来说明.md`
- `wcy_C4D_output_logs/`：分步运行日志（计划 / 地点生成 / 修正 / 最终地点）

## 技术要点

- 本地模型：`gemma4:e4b`（Q4_K_M 量化，6.6 GB），Ollama 0.35.1
- 运行设备：Mac mini（Apple M4 10 核 CPU + 10 核 GPU，16 GB，macOS）
- 地图地点数据 100% 由本地大模型生成，未调用云端 LLM API
- Level 1 对话示例：453 tokens / 31.20s（18.67 tok/s）；Level 2 分步生成 + 校正 + Folium 出图

## 复现方式

见 `wcy_C4D_教学说明.md`。
