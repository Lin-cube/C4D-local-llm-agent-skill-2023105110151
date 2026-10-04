# Demo —— C4D 本地大模型 Agent 技能演示材料

本目录是 C4D 挑战的**可复现演示包**：包含运行录屏、关键截图，以及一步步复现的命令。
所有画面均来自本机真实运行，使用本地 Ollama 模型 `gemma4:e4b`，全程未调用云端大模型 API。

## 1. 演示视频

| 文件 | 时长/大小 | 内容 |
|------|-----------|------|
| `演示录屏.mp4` | 约 12 MB | 终端运行 `02_level2_agent_map.py` 的完整过程：模型规划 → 生成地点 → 坐标校验 → 渲染地图，然后浏览器打开 `wcy_C4D_map.html`，缩放并点击标记查看双语弹窗 |

## 2. 关键截图

| 文件 | 证明什么 |
|------|----------|
| `截图_设备与环境.png` | 运行设备与本地环境（macOS / Apple M4 / Ollama 版本） |
| `截图_本地模型调用.png` | 本地模型 `gemma4:e4b` 已被调用并加载（`ollama list` / `ollama ps`） |
| `截图_推理速度.png` | 本地推理速度（`xx.xx tok/s`），对应 Level 1 脚本输出 |
| `截图_交互式地图.png` | Agent 最终产物：带彩色分类标记与中英双语弹窗的交互式地图 |

## 3. 复现步骤（约 3 分钟）

```bash
# ① 准备本地模型运行时
ollama pull gemma4:e4b          # 约 6.6 GB，Q4_K_M 量化

# ② 安装 Python 依赖
pip3 install folium requests

# ③ Level 1：本地对话连通性 + 推理速度
python3 ../Agent技能/01_level1_chat.py
#     → 终端出现 "模型: gemma4:e4b" 与 "速度 xx.xx tok/s"

# ④ Level 2：完整 Agent 工作流，产出交互式地图
python3 ../Agent技能/02_level2_agent_map.py
#     → 生成 ../wcy_C4D_map.html

# ⑤ 打开地图，缩放并点击任意标记查看双语弹窗
open ../wcy_C4D_map.html         # macOS；Windows 用 start，Linux 用 xdg-open
```

## 4. 如何验证「确实是本地模型」

1. 断开网络后重跑 ③ ④ —— 模型推理与 Agent 逻辑仍可完成（只有底图瓦片需要联网）；
2. 终端执行 `ollama ps`，可见 `gemma4:e4b` 处于 loaded 状态；
3. 对照 `../wcy_C4D_output_logs/step2_locations_raw.json` —— 地点数据是模型的原始输出，未经人工改写；
4. `../wcy_C4D_output_logs/run_proof.txt` 保留了完整运行回显，可与录屏逐帧对应。

## 5. 目录对应关系

| 交付物 | 位置 |
|--------|------|
| Agent 技能（可运行代码包） | `../Agent技能/`（含 SKILL.md、两个脚本、依赖锁） |
| Demo（录屏 + 截图 + 复现步骤） | 本目录 |
| AI 日志 | `../wcy_C4D_output_logs/`、`../wcy_C4D_AI日志.md` |
| AAR 复盘 | `../wcy_C4D_AAR.md` |
