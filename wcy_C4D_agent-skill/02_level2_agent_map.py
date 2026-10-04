# -*- coding: utf-8 -*-
"""
C4D 挑战 - Level 2：本地 Gemma 4 Agent（多步推理 + 结构化输出 + 交互式地图）
==========================================================================
Agent 工作流（全部由本地模型驱动，零 API 费用）：
    第 1 步  规划：让模型先制定"生成地图"的行动计划（多步推理）
    第 2 步  生成：让模型用结构化 JSON 输出 8 个西亚斯学院周边地点
    第 3 步  校验：Agent 代码检查坐标是否落在新郑市范围内（工具调用式校验），
             不合格的坐标让模型自己修正（第二轮函数式交互）
    第 4 步  渲染：用 Folium 生成交互式 HTML 地图（可缩放、可点击标记）
运行方式：python3 02_level2_agent_map.py
"""

# ======================= 第 1 部分：导入库 =======================
import json      # JSON 解析：模型输出的结构化数据要转成 Python 对象
import time      # 计时：记录每一步耗时和推理速度
import re        # 正则表达式：从模型输出里"捞"出 JSON 部分（模型有时会说多余的话）
import requests  # HTTP 请求：和本地 Ollama 服务通信
import folium    # 交互式地图：一行代码生成 Leaflet 地图 HTML

# ======================= 第 2 部分：全局配置 =======================
OLLAMA_CHAT = "http://localhost:11434/api/chat"  # Ollama 聊天接口
MODEL_NAME  = "gemma4:e4b"                        # 本地模型（按实际拉取的模型修改）
LOG_DIR     = "../wcy_C4D_output_logs"            # 日志目录：保存模型每一步的原始输出
MAP_FILE    = "../wcy_C4D_map.html"               # 最终生成的交互式地图

# 新郑市（西亚斯学院所在地）的大致经纬度范围，用来校验模型给的坐标是否靠谱
# 格式：[最小纬度, 最大纬度, 最小经度, 最大经度]
XINZHENG_BBOX = [34.30, 34.60, 113.60, 113.90]


# ======================= 第 3 部分：封装"调用本地模型"函数 =======================
def call_model(messages, force_json=False):
    """
    调用本地 Ollama 模型并返回 (回复文本, 性能统计)。
    messages  : 对话历史列表
    force_json: True 时强制模型只输出合法 JSON（Ollama 的 format 参数）
    """
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,                  # 非流式：等结果全部生成再返回
        "options": {"temperature": 0.4},  # 温度低一点，输出更稳定、更适合结构化数据
    }
    if force_json:
        payload["format"] = "json"        # 关键参数：强制 JSON 结构化输出（Agent 能力之一）

    start = time.time()
    resp = requests.post(OLLAMA_CHAT, json=payload, timeout=600)
    resp.raise_for_status()
    data = resp.json()

    # 统计推理速度 tok/s（评审要求展示的关键指标）
    eval_count = data.get("eval_count", 0)
    eval_dur   = data.get("eval_duration", 1) / 1e9
    stats = {
        "elapsed_sec": round(time.time() - start, 2),
        "eval_count": eval_count,
        "tok_s": round(eval_count / eval_dur, 2) if eval_dur > 0 else 0,
    }
    return data["message"]["content"], stats


def extract_json(text):
    """从模型回复中提取 JSON（模型偶尔会在 JSON 前后加解释文字，用正则兜底）"""
    # 先尝试直接解析整段文本
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 兜底：用正则找第一个 { 或 [ 开始、最后一个 } 或 ] 结束的片段
    match = re.search(r"[\[{].*[\]}]", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError(f"模型输出不是合法 JSON:\n{text[:500]}")


def save_log(name, content):
    """把每一步的原始输出保存到日志目录，作为'模型输出日志'交付物"""
    path = f"{LOG_DIR}/{name}"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    print(f"   [日志已保存] {path}")


# ======================= 第 4 步（步骤 1）：让模型制定行动计划 =======================
print("=" * 60)
print("步骤 1/4：Agent 规划——让本地模型制定行动计划")
print("=" * 60)

plan_messages = [
    {"role": "system", "content": "你是一个地图生成 Agent，请用中文思考。"},
    {"role": "user", "content": (
        "我要为郑州西亚斯学院（SIAS University）生成一张周边地图。"
        "请列出你计划标注的 8 个地点名称（校园内建筑优先），"
        "并以 JSON 格式返回：{\"plan\": [\"地点1\", \"地点2\", ...]}"
    )},
]

plan_reply, plan_stats = call_model(plan_messages, force_json=True)
plan_data = extract_json(plan_reply)
print(f"模型规划：{plan_data.get('plan', plan_data)}")
print(f"   性能：{plan_stats['elapsed_sec']}s / {plan_stats['tok_s']} tok/s")
save_log("step1_plan.json", {"stats": plan_stats, "raw": plan_reply, "parsed": plan_data})

# ======================= 第 5 步（步骤 2）：让模型生成结构化地点数据 =======================
print("\n" + "=" * 60)
print("步骤 2/4：Agent 生成——让本地模型输出结构化地点 JSON")
print("=" * 60)

gen_messages = [
    {"role": "system", "content": (
        "You are a geography assistant. Always respond with valid JSON only. "
        "坐标请尽量接近真实位置（新郑市，河南，中国，中心约 34.40N, 113.73E）。"
    )},
    {"role": "user", "content": (
        "针对以下 8 个地点，生成 JSON 数组，每个元素包含字段："
        'name（英文）、name_zh（中文）、latitude（纬度，数字）、longitude（经度，数字）、'
        "description（30 字以内中文描述）、category（教学/生活/体育/地标之一）。\n"
        f"地点列表：{json.dumps(plan_data.get('plan', []), ensure_ascii=False)}"
    )},
]

gen_reply, gen_stats = call_model(gen_messages, force_json=True)
locations = extract_json(gen_reply)
# 兼容两种情况：模型直接返回数组，或包在某个键里
if isinstance(locations, dict):
    for key in ("locations", "places", "data", "items"):
        if key in locations:
            locations = locations[key]
            break
print(f"模型返回 {len(locations)} 个地点")
print(f"   性能：{gen_stats['elapsed_sec']}s / {gen_stats['tok_s']} tok/s")
save_log("step2_locations_raw.json", {"stats": gen_stats, "raw": gen_reply, "parsed": locations})

# ======================= 第 6 步（步骤 3）：Agent 校验 + 让模型自我修正 =======================
print("\n" + "=" * 60)
print("步骤 3/4：Agent 校验——检查坐标是否落在新郑市范围内，越界则让模型修正")
print("=" * 60)


def is_in_bbox(loc):
    """工具函数：判断一个地点的坐标是否在新郑市范围内"""
    lat, lng = loc.get("latitude", 0), loc.get("longitude", 0)
    return XINZHENG_BBOX[0] <= lat <= XINZHENG_BBOX[1] and \
           XINZHENG_BBOX[2] <= lng <= XINZHENG_BBOX[3]


bad = [loc.get("name_zh", loc.get("name", "?")) for loc in locations if not is_in_bbox(loc)]
if bad:
    # 坐标越界 -> 把校验结果"反馈"给模型，让它第二轮修正（这就是带反馈的多步推理）
    print(f"   发现 {len(bad)} 个坐标越界：{bad}，请求模型修正...")
    fix_messages = gen_messages + [
        {"role": "assistant", "content": gen_reply},
        {"role": "user", "content": (
            f"以下地点的经纬度超出了新郑市合理范围（纬度 34.30-34.60，经度 113.60-113.90）："
            f"{json.dumps(bad, ensure_ascii=False)}。"
            "请只输出修正后的完整 JSON 数组（格式不变），把越界坐标调整到合理范围。"
        )},
    ]
    fix_reply, fix_stats = call_model(fix_messages, force_json=True)
    fixed = extract_json(fix_reply)
    if isinstance(fixed, dict):
        for key in ("locations", "places", "data", "items"):
            if key in fixed:
                fixed = fixed[key]
                break
    if isinstance(fixed, list) and len(fixed) == len(locations):
        locations = fixed          # 修正成功，用新数据替换
    save_log("step3_fix.json", {"stats": fix_stats, "raw": fix_reply, "parsed": fixed})
    print(f"   修正后性能：{fix_stats['elapsed_sec']}s / {fix_stats['tok_s']} tok/s")
else:
    print("   所有坐标均在合理范围内，无需修正")
    save_log("step3_fix.json", {"note": "无需修正，所有坐标均在范围内"})

# 兜底：如果个别坐标仍然离谱，直接夹紧到范围内（保证地图一定可用）
for loc in locations:
    loc["latitude"] = max(XINZHENG_BBOX[0], min(XINZHENG_BBOX[1], float(loc["latitude"])))
    loc["longitude"] = max(XINZHENG_BBOX[2], min(XINZHENG_BBOX[3], float(loc["longitude"])))

save_log("step4_final_locations.json", locations)

# ======================= 第 7 步（步骤 4）：用 Folium 渲染交互式地图 =======================
print("\n" + "=" * 60)
print("步骤 4/4：渲染交互式地图（Folium / Leaflet）")
print("=" * 60)

# 地图中心取所有地点坐标的平均值，缩放级别 14 大约能看到整个校园
center_lat = sum(loc["latitude"] for loc in locations) / len(locations)
center_lng = sum(loc["longitude"] for loc in locations) / len(locations)
m = folium.Map(location=[center_lat, center_lng], zoom_start=15, tiles="OpenStreetMap")

# 不同类别用不同颜色的标记，提升地图可读性
COLORS = {"教学": "blue", "生活": "green", "体育": "orange", "地标": "purple"}

for loc in locations:
    color = COLORS.get(loc.get("category", ""), "red")
    popup_html = (
        f"<b>{loc.get('name_zh', loc.get('name', '地点'))}</b> "
        f"<span style='color:gray'>({loc.get('name', '')})</span><br>"
        f"类别：{loc.get('category', '未分类')}<br>"
        f"坐标：{loc['latitude']:.5f}, {loc['longitude']:.5f}<br>"
        f"{loc.get('description', '')}"
    )
    folium.Marker(
        [loc["latitude"], loc["longitude"]],                     # 标记位置
        popup=folium.Popup(popup_html, max_width=260),           # 点击弹出的信息窗
        tooltip=loc.get("name_zh", loc.get("name", "")),         # 鼠标悬停提示
        icon=folium.Icon(color=color, icon="graduation-cap", prefix="fa"),  # 彩色图标
    ).add_to(m)

# 添加图层开关和标题，让地图更专业
folium.LayerControl().add_to(m)
title = folium.Element(
    "<div style='position:fixed;top:10px;left:50%;transform:translateX(-50%);z-index:9999;"
    "background:white;padding:8px 16px;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,.3);"
    "font-size:16px;font-weight:bold;'>"
    "郑州西亚斯学院（SIAS University）周边地图 · 由本地 Gemma 4 Agent 生成"
    "</div>"
)
m.get_root().html.add_child(title)

m.save(MAP_FILE)
print(f"\n地图已生成: {MAP_FILE}")
print(f"共 {len(locations)} 个标记点，全部数据由本地 {MODEL_NAME} 生成")
