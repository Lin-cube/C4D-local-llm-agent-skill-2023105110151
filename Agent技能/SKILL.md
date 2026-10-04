---
name: c4d-local-llm-map-agent
description: 用本地 Ollama 模型 gemma4:e4b 驱动 Agent，按「规划 → 生成 → 校验 → 渲染」四步生成郑州西亚斯学院周边交互式地图；全程离线推理，不调用任何云端大模型 API。
version: 1.0.0
runtime: python >= 3.13
dependencies:
  - ollama >= 0.35.1（本地模型运行时）
  - requests
  - folium
---

# C4D Agent 技能 —— 本地大模型地图生成

## 这个技能能做什么

给一句自然语言指令（例：`生成西亚斯学院周边地图`），Agent 会自己完成四步，
最后产出一个可直接用浏览器打开的交互式地图 HTML：

```
用户指令
   ↓
① 规划 Plan      以 format=json 约束模型，输出 {"plan": ["地点1", ...]}（8 个地点）
   ↓
② 生成 Generate  模型输出 8×6 字段结构化地点数据（中英文名 / 经纬度 / 描述 / 分类）
   ↓
③ 校验 Verify    Agent 工具函数：bbox 检查坐标是否落在新郑市范围
                  └ 越界 → 把校验失败原因回传模型，触发第二轮自我修正
   ↓
④ 渲染 Render    folium → Leaflet 交互式地图（彩色分类标记 + 中英双语弹窗 + 图层控制）
```

中间产物全部落盘到 `../wcy_C4D_output_logs/`，这就是 Agent 的「记忆 / 可追溯输出」。

## 前置条件

1. 已安装 [Ollama](https://ollama.com) 并可执行 `ollama` 命令；
2. 已拉取本地模型：`ollama pull gemma4:e4b`（约 6.6 GB，Q4_K_M 量化，4.5B 有效参数）；
3. Python ≥ 3.13，安装依赖：`pip3 install folium requests`。

> 推理本身完全离线（本地 `http://localhost:11434`）。
> 只有最后查看地图时，浏览器会联网加载 OpenStreetMap 底图瓦片。

## 使用方式

```bash
# Level 1 —— 本地对话连通性验证（顺带打印推理速度 tok/s）
python3 01_level1_chat.py

# Level 2 —— 完整 Agent 工作流，生成交互式地图
python3 02_level2_agent_map.py
# 产出：../wcy_C4D_map.html（浏览器打开即可交互）
```

## 文件清单

| 文件 | 说明 |
|------|------|
| `01_level1_chat.py` | Level 1：调用本地模型生成西亚斯学院介绍，并输出推理速度 |
| `02_level2_agent_map.py` | Level 2：四步 Agent 工作流，逐行中文注释 |
| `pyproject.toml` / `uv.lock` | 依赖声明与锁定（可用 uv 一键复现环境） |
| `README.md` | 快速开始与工作流说明 |

## 输入 / 输出契约

| 阶段 | 输入 | 输出（落盘文件） |
|------|------|------------------|
| ① 规划 | system 提示 + 用户指令 | `step1_plan.json` |
| ② 生成 | 规划结果 | `step2_locations_raw.json` |
| ③ 校验 | 坐标 bbox(34.30–34.60N, 113.60–113.90E) | `step3_fix.json` |
| ④ 渲染 | 修正后坐标 | `step4_final_locations.json` + `../wcy_C4D_map.html` |

另有 `run_proof.txt`（完整运行回显）与 `level1_chat_log.json`（对话日志）作为 AI 使用记录的佐证。

## 已知限制与取舍

- **速度**：本地 gemma4:e4b 单次生成明显慢于云端 API，属预期取舍（换来零成本、零数据外传）；
- **质量**：小模型的坐标精度有限，因此额外加了 bbox 校验 + 自我修正这一环，而不是直接信任一次输出；
- **联网**：仅底图瓦片需要网络，模型推理与 Agent 逻辑全部离线可跑。
