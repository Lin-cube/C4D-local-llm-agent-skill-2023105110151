# C4D 教学说明 —— 从零安装到复现（保姆级）

> 照着做，你就能在自己的 Mac 上复现这个本地 Agent。全程约 30 分钟（大部分时间在下载模型）。

---

## 第 0 步：确认你的设备

本方案适配 **Apple Silicon（M1–M4）+ 16GB 内存** 的 Mac。
8GB 内存请改用 `gemma4:e2b`；24GB+ 可尝试 `gemma4:26b`。

## 第 1 步：安装 Ollama（5 分钟）

方式 A —— Homebrew（推荐）：

```bash
brew install ollama
```

方式 B —— 官网下载安装包：
打开 https://ollama.com/download/mac ，下载 zip，解压拖进"应用程序"。

## 第 2 步：启动 Ollama 服务

```bash
# 方式 A：只启动一次（关终端就停）
ollama serve

# 方式 B：注册为系统服务（开机自启）
brew services start ollama
```

验证服务已启动（应输出版本号，如 `{"version":"0.35.1"}`）：

```bash
curl http://localhost:11434/api/version
```

## 第 3 步：下载 Gemma 4 模型（约 6.6 GB，视网速 10–30 分钟）

```bash
ollama pull gemma4:e4b
```

下载完确认：

```bash
ollama list
# 应看到: gemma4:e4b  dc35e8d9c606  6.6 GB
```

> 💡 也可以先 `ollama run gemma4:e4b` 直接进入命令行聊天体验一下，
> 输入 `/bye` 退出。截图证明要求：聊天界面要能看到模型名。

## 第 4 步：安装 Python 依赖（1 分钟）

本技能只需要两个库：

```bash
pip3 install folium requests
```

## 第 5 步：运行 Agent 技能

```bash
# 进入技能目录（按你的实际路径修改）
cd wcy_C4D_agent-skill

# Level 1：本地对话验证（生成西亚斯学院介绍，输出速度 tok/s）
python3 01_level1_chat.py

# Level 2：Agent 四步工作流 → 生成交互式地图
python3 02_level2_agent_map.py
```

> ⚠️ 注意：如果两个脚本的模型名和你的不一致，请把脚本开头的
> `MODEL_NAME = "gemma4:e4b"` 改成 `ollama list` 里显示的名字。

## 第 6 步：查看结果

- 运行日志保存在 `../wcy_C4D_output_logs/`（每一步的模型原始输出 + 性能数据）
- 地图生成在上层目录 `wcy_C4D_map.html`，双击用浏览器打开：

```bash
open ../wcy_C4D_map.html
```

地图操作：滚轮缩放、拖动平移、点击彩色标记看双语信息窗。

## 第 7 步：截取证明截图（提交需要）

建议截 3 张图，必须清晰包含以下信息：

1. **终端里运行 `ollama list` 和 `ollama ps`** —— 证明模型名称/版本 + 100% GPU 本地推理
2. **脚本运行中的输出** —— 包含模型名和 tok/s 推理速度
3. **浏览器中打开的地图** —— 左下角 Leaflet 出现即证明是本地 HTML

Mac 截图快捷键：`Cmd + Shift + 4`（区域截图），文件默认在桌面。

## 常见问题

| 问题 | 解决 |
|------|------|
| `Connection refused` | Ollama 服务没启动，先跑 `ollama serve` |
| 下载很慢 | Ollama 支持断点续传，中断后重新 `ollama pull` 即可 |
| 内存不足 / 系统卡顿 | 换小模型：把脚本里模型名改成 `gemma4:e2b` |
| 地图打不开/空白 | 检查网络（Leaflet 底图需要联网加载，模型本身不需要） |
