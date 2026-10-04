# C4D Agent 技能包 —— 本地 Gemma 4 Agent

用本地运行的 `gemma4:e4b` 模型（Ollama）驱动 Agent，
自动规划 → 生成结构化地点数据 → 校验坐标 → 渲染郑州西亚斯学院交互式地图。

## 快速开始

```bash
# 0. 前置：已安装 Ollama 并拉取模型
ollama pull gemma4:e4b

# 1. 安装依赖
pip3 install folium requests

# 2. Level 1：本地对话验证
python3 01_level1_chat.py

# 3. Level 2：Agent 生成地图（输出到上层目录 wcy_C4D_map.html）
python3 02_level2_agent_map.py
```

详细步骤见上层目录《wcy_C4D_教学说明.md》。

## 文件说明

| 文件 | 说明 |
|------|------|
| `01_level1_chat.py` | Level 1：调用本地模型生成西亚斯学院介绍，输出推理速度 |
| `02_level2_agent_map.py` | Level 2：四步 Agent 工作流（规划→生成→校验→渲染），逐行中文注释 |

## Agent 工作流

```
用户指令 "生成西亚斯学院周边地图"
    ↓
① 规划   format=json → 模型输出 {"plan": [8 个地点]}
    ↓
② 生成   模型输出 8×6 字段地点 JSON（中英文名/坐标/描述/分类）
    ↓
③ 校验   Agent 工具：bbox 检查坐标是否在新郑市范围
         └ 越界 → 把校验结果回传模型，第二轮自我修正
    ↓
④ 渲染   Folium → Leaflet 交互式地图（彩色分类标记 + 双语弹窗）
```

所有中间输出保存到 `../wcy_C4D_output_logs/`，作为模型输出日志交付物。
