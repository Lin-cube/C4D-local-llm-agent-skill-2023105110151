# -*- coding: utf-8 -*-
"""
C4D 挑战 - Level 1：本地跑通 Gemma 4 基本对话
================================================
作用：验证本地 Ollama + Gemma 4 模型已经能正常对话，
     并让模型生成一段关于郑州西亚斯学院（SIAS University）的介绍文字。
运行前提：Ollama 已安装并正在运行（终端执行 `ollama serve` 或点击 Ollama 图标）
运行方式：python3 01_level1_chat.py
"""

# ---------- 第 1 部分：导入需要的库 ----------
import json      # 用来把 Python 字典转换成 JSON 文本、或把 JSON 文本解析回字典
import time      # 用来计算模型响应耗时
import requests  # 用来向本地 Ollama 服务发送 HTTP 请求

# ---------- 第 2 部分：定义全局配置 ----------
OLLAMA_URL = "http://localhost:11434/api/chat"  # Ollama 本地聊天接口的地址（11434 是它的默认端口）
MODEL_NAME = "gemma4:e4b"                        # 我们使用的本地模型名称和版本（按实际拉取的模型修改）
LOG_FILE   = "../wcy_C4D_output_logs/level1_chat_log.json"  # 运行结果保存位置，方便写进 AI 日志和截图证明

# ---------- 第 3 部分：构造对话内容 ----------
# messages 是"对话历史"列表，每个元素是一个字典：
#   role 取值：system（给模型的身份设定）/ user（用户说的话）/ assistant（模型的回答）
messages = [
    {
        "role": "system",
        # 系统提示：告诉模型它是谁、应该怎么回答
        "content": "你是一位熟悉中国高校的地理助手，请用中文回答。"
    },
    {
        "role": "user",
        # 用户指令：挑战要求让模型生成一段 SIAS University 的介绍
        "content": "请用大约 150 字介绍郑州西亚斯学院（SIAS University）：它的位置、办学特色和校园环境。"
    }
]

# ---------- 第 4 部分：把请求体打包 ----------
# Ollama 的 /api/chat 接口需要收到一个 JSON 对象，包含：
#   model     -> 用哪个模型
#   messages  -> 对话历史
#   stream    -> 是否流式输出（False = 等全部生成完再一次性返回，方便统计）
payload = {
    "model": MODEL_NAME,
    "messages": messages,
    "stream": False
}

# ---------- 第 5 部分：发送请求并计时 ----------
print(f">>> 正在调用本地模型 {MODEL_NAME}（完全离线，不消耗任何 API 费用）...")
start = time.time()                      # 记录开始时间
# requests.post 的第一个参数是网址，json= 参数会自动把字典转成 JSON 发出去
response = requests.post(OLLAMA_URL, json=payload, timeout=300)
elapsed = time.time() - start            # 计算总耗时（秒）
response.raise_for_status()              # 如果 HTTP 状态码不是 200，直接抛出错误

# ---------- 第 6 部分：解析返回结果 ----------
# Ollama 返回的 JSON 里：
#   message.content -> 模型生成的文字
#   eval_count      -> 本次生成的 token 数量
#   eval_duration   -> 生成阶段耗时（纳秒）
data = response.json()
reply = data["message"]["content"]
eval_count = data.get("eval_count", 0)                # 生成了多少个 token
eval_dur   = data.get("eval_duration", 1) / 1e9       # 纳秒换算成秒
tok_s      = eval_count / eval_dur if eval_dur > 0 else 0  # 推理速度（token/秒），这是评审要求的关键指标

# ---------- 第 7 部分：打印结果 ----------
print(f"\n===== 模型回答 =====\n{reply}")
print(f"\n===== 性能数据 =====")
print(f"模型: {MODEL_NAME}")
print(f"总耗时: {elapsed:.2f} 秒 | 生成 {eval_count} tokens | 速度 {tok_s:.2f} tok/s")

# ---------- 第 8 部分：保存日志 ----------
log = {
    "model": MODEL_NAME,
    "messages": messages,
    "reply": reply,
    "elapsed_sec": round(elapsed, 2),
    "eval_count": eval_count,
    "tok_s": round(tok_s, 2),
}
# 用 with 打开文件可以在结束时自动关闭；ensure_ascii=False 让中文原样保存而不是转成 \uXXXX
with open(LOG_FILE, "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)
print(f"\n日志已保存: {LOG_FILE}")
