import json
import os
import re
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AGENT_PATH = ROOT / "AGENTS.md"
HTML_PATH = ROOT / "storyboard-workflow.html"
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8787"))


LENS_PLAN = [
    ("远景", "平视略低机位", "固定轻推", "交代环境", "建立空间方向与角色起点"),
    ("中全景", "正面平视", "横移跟拍", "推进动作", "展示动作起因与身体方向"),
    ("半身近景", "正面略仰", "慢速推进", "强化情绪", "聚焦表情、手部和上半身动作"),
    ("近景", "侧前方 30 度", "轻微横移", "揭示信息", "衔接上一镜动作的关键细节"),
    ("特写", "正面平视", "固定镜头", "强化情绪", "突出眼神、道具、发丝或手部细节"),
    ("中近景", "正面略低", "快速推进后固定", "完成转折", "完成动作结果与高光定格"),
]


def read_agent_rules():
    if not AGENT_PATH.exists():
        return "未找到 AGENTS.md，使用内置故事板规则。"
    return AGENT_PATH.read_text(encoding="utf-8", errors="replace")


def split_script(text):
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if not cleaned:
        return []
    parts = [p.strip() for p in re.split(r"(?<=[。！？!?；;])|[\r\n]+", cleaned) if p.strip()]
    if len(parts) >= 4:
        return parts
    return [p.strip() for p in re.split(r"[，,、]", cleaned) if p.strip()]


def normalize_cut_count(parts, group_size):
    count = max(group_size, min(18, len(parts) or group_size))
    if len(parts) >= count:
        return parts[:count]
    fillers = [
        "建立主要场景与人物状态",
        "角色进入动作，形成清楚的运动方向",
        "推进关键动作，保持动作匹配剪辑",
        "进入情绪近景，强调眼神和手部细节",
        "完成动作转折或队形变化",
        "以高光定格收束本组镜头",
    ]
    out = list(parts)
    while len(out) < count:
        out.append(fillers[len(out) % len(fillers)])
    return out


def number_from_duration(duration_text):
    match = re.search(r"\d+(?:\.\d+)?", duration_text or "")
    return float(match.group(0)) if match else 15.0


def trim_num(value):
    return str(int(value)) if float(value).is_integer() else f"{value:.1f}"


def time_range(index, total, duration_text):
    duration = number_from_duration(duration_text)
    start = round((duration / total) * index, 1)
    end = round((duration / total) * (index + 1), 1)
    return f"{trim_num(start)}-{trim_num(end)}s"


def action_keyword(text, index):
    presets = ["起势", "推进", "抬手", "转身", "眼神", "定格"]
    words = [w for w in re.split(r"[。！？!?，,；;、\s]+", text or "") if w]
    short = next((w for w in words if 2 <= len(w) <= 8), "")
    return f"{short} / {presets[index % len(presets)]}" if short else f"{presets[index % len(presets)]} / 情绪推进"


def collect_refs(refs):
    active = []
    for i, item in enumerate(refs or [], 1):
        role = item.get("role") or "参考图"
        name = item.get("name") or "未上传"
        desc = item.get("desc") or ""
        if name != "未上传" or desc:
            line = f"图{i}（{role}）：{name}"
            if desc:
                line += f"。{desc}"
            active.append(line)
    if not active:
        return "无参考图，根据剧本统一设计人物与场景，但必须保持每个分镜连续一致。"
    return "\n".join(active)


def api_is_enabled(payload):
    api = resolve_api_config(payload)
    return bool(api.get("enabled") and api.get("baseUrl") and api.get("model") and api.get("apiKey"))


def env_truthy(name):
    return (os.getenv(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def resolve_api_config(payload):
    user_api = payload.get("api") or {}
    env_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
    env_base = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    env_model = os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL") or ""
    enabled = bool(user_api.get("enabled")) or env_truthy("STORYBOARD_LLM_ENABLED")
    return {
        "enabled": enabled,
        "baseUrl": user_api.get("baseUrl") or env_base,
        "model": user_api.get("model") or env_model,
        "apiKey": user_api.get("apiKey") or env_key,
    }


def chat_completion(api, messages, temperature=0.35):
    base_url = (api.get("baseUrl") or "").rstrip("/")
    if not base_url:
        raise ValueError("missing API Base URL")
    url = base_url if base_url.endswith("/chat/completions") else f"{base_url}/chat/completions"
    body = {
        "model": api.get("model"),
        "messages": messages,
        "temperature": temperature,
    }
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api.get('apiKey')}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"]


def parse_json_object(text):
    raw = (text or "").strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I | re.S).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def llm_analyze_script(payload, include_parts=False):
    if not api_is_enabled(payload):
        return None
    api = resolve_api_config(payload)
    group_size = int(payload.get("groupSize") or 5)
    duration = payload.get("duration") or "15s"
    script = payload.get("script") or ""
    refs = collect_refs(payload.get("refs", []))
    parts_rule = (
        f"\n同时输出 parts：把剧本拆成 {group_size}-18 个连续动作片段，用于分镜 Cut 动作。"
        if include_parts
        else ""
    )
    user_prompt = f"""请分析以下 MV / 短片剧本，输出严格 JSON，不要解释，不要 Markdown。
字段：
- character：剧本中出现的人物设定，必须包含角色名称、外貌特征、服装、体态、年龄、气质、一致性要求。
- scene：剧本中出现的场景设定，必须明确是什么场景，并包含建筑结构、空间方向、材质、灯光、道具、入口、角色行动区域、一致性要求。{parts_rule}

总时长：{duration}
参考图信息：
{refs}

剧本：
{script}
"""
    content = chat_completion(
        api,
        [
            {"role": "system", "content": "你是专业影视分镜故事板分析师，只输出可解析 JSON。"},
            {"role": "user", "content": user_prompt},
        ],
    )
    parsed = parse_json_object(content)
    if not isinstance(parsed, dict):
        return None
    return parsed


def infer_character_setting(script, has_refs=False):
    # 如果没有参考图，返回空字符串
    if not has_refs:
        return ""

    text = re.sub(r"\s+", " ", script or "").strip()
    if not text:
        return "核心角色：根据剧本主体统一设计，保持同一人物的五官、发型、服装、体型、年龄和气质连续一致。"

    role_patterns = [
        ("女团成员", r"女团成员|女爱豆|女偶像|舞者|女孩|少女|女人|女主|她"),
        ("男主角", r"男主|男人|男孩|少年|他"),
        ("记者", r"记者|媒体|摄影师|采访者"),
        ("保镖", r"保镖|安保|护卫"),
        ("观众", r"观众|人群|路人|围观者"),
    ]
    roles = []
    for name, pattern in role_patterns:
        if re.search(pattern, text) and name not in roles:
            roles.append(name)
    if not roles:
        roles.append("核心角色")

    feature_map = [
        ("黑色长发", r"黑色长发|长直发|黑发|长发"),
        ("齐刘海", r"齐刘海|刘海"),
        ("红色短夹克", r"红色夹克|红色短夹克|红外套"),
        ("白色上衣", r"白色上衣|白色背心|白色短背心|白裙|白色服装"),
        ("黑色工装裤", r"黑色工装裤|黑裤|工装裤"),
        ("银色礼服", r"银色礼服|银色裙|金属银"),
        ("高冷模特气质", r"高冷|冷艳|冷感|疏离|帅酷|模特范"),
        ("妩媚可爱气质", r"妩媚|可爱|撩头发|甜美"),
        ("年轻亚洲女性", r"女团|女孩|少女|女人|女主|她"),
    ]
    features = [label for label, pattern in feature_map if re.search(pattern, text)]
    if not features:
        features = ["根据剧本动作和情绪联想外貌特征", "五官清晰", "发型服装统一", "气质与剧情一致"]

    primary = roles[0]
    lines = [f"{primary}：{ '，'.join(features) }。"]
    if len(roles) > 1:
        lines.append("其他人物：" + "、".join(roles[1:]) + "，只作为剧情需要的配角或环境人物，外貌与站位保持前后统一。")
    lines.append("所有角色在每个 Cut 中必须保持同一身份、五官、发型、服装、体态、年龄和气质一致。")
    return "\n".join(lines)


def infer_scene_setting(script, has_refs=False):
    # 如果没有参考图，返回空字符串
    if not has_refs:
        return ""

    text = re.sub(r"\s+", " ", script or "").strip()
    if not text:
        return "核心场景：根据剧本统一设计一个连续空间，明确入口、纵深、主光方向、道具位置和角色行动区域。"

    scene_map = [
        ("纯白未来走廊", r"未来走廊|白色走廊|纯白|线性灯|LED|镜面地面"),
        ("夜晚霓虹街角", r"夜晚|霓虹|街角|街道|路口|车|招牌"),
        ("复古街边士多店", r"士多店|便利店|街边小店|可乐|冰柜|店铺"),
        ("城市楼顶舞台", r"楼顶|屋顶|城市高空|天台|环形舞台"),
        ("红毯媒体区", r"红毯|颁奖|记者|媒体|闪光灯|名利场"),
        ("室内舞台空间", r"舞台|摄影棚|灯光阵列|演出空间"),
    ]
    scenes = [name for name, pattern in scene_map if re.search(pattern, text)]
    if not scenes:
        scenes = ["剧本核心场景"]

    props = []
    prop_map = [
        ("线性灯带", r"线性灯|灯带|LED"),
        ("镜面反光地面", r"镜面|反光地面|地面反射"),
        ("霓虹招牌", r"霓虹|招牌"),
        ("车辆", r"车|汽车|跑车"),
        ("话筒和相机", r"话筒|相机|摄影机|记者"),
        ("冰柜和饮料箱", r"冰柜|可乐|饮料|货架"),
    ]
    for label, pattern in prop_map:
        if re.search(pattern, text):
            props.append(label)
    if not props:
        props = ["关键道具按剧本动作统一摆放"]

    return (
        f"主要场景：{scenes[0]}。"
        f"空间要求：明确入口、背景纵深、主机位方向、角色起点与终点、行动路径和安全留白。"
        f"道具与材质：{ '，'.join(props) }。"
        "光源方向、建筑结构、空间方向、材质和氛围必须在所有 Cut 中保持一致。"
    )


def build_shots(payload):
    group_size = int(payload.get("groupSize") or 5)
    llm_parts = payload.get("_shotParts")
    if isinstance(llm_parts, list):
        raw_parts = [str(part).strip() for part in llm_parts if str(part).strip()]
    else:
        raw_parts = split_script(payload.get("script", ""))
    parts = normalize_cut_count(raw_parts, group_size)
    total = len(parts)
    shots = []
    for index, part in enumerate(parts):
        plan = LENS_PLAN[min(index, len(LENS_PLAN) - 1)]
        is_last = index == total - 1
        shot = {
            "cut": f"Cut{index + 1}",
            "time": time_range(index, total, payload.get("duration", "15s")),
            "functionName": "完成转折" if is_last else plan[3],
            "shotSize": plan[0],
            "angle": plan[1],
            "camera": "快速推进后固定" if is_last else plan[2],
            "blocking": f"保持同一轴线与空间方向；角色从上一镜动作自然延续，视线与运动方向清楚；{plan[4]}。",
            "subject": "核心角色、关键道具、当前场景环境元素",
            "action": part,
            "description": f"围绕“{part}”设计画面：先保证主体清晰，再用构图、光影和背景关系强化情绪；每镜保留 1-2 个视觉重点，动作与上一镜连续。",
            "dialogue": "无",
            "sound": "音乐强拍、环境声回落、动作停顿" if is_last else "环境声、动作声、音乐节拍",
            "rhythm": "爆发 / 定格" if is_last else ["缓慢", "律动", "紧张", "聚焦", "压迫"][index % 5],
            "keyword": action_keyword(part, index),
        }
        shots.append(shot)
    return shots


def chunk_shots(shots, size):
    return [shots[i : i + size] for i in range(0, len(shots), size)]


def build_storyboard_prompt(payload, group, group_index, agent_rules):
    title = payload.get("projectTitle") or "MV舞蹈分镜故事板"
    duration = payload.get("duration") or "15s"
    ratio = payload.get("ratio") or "3:4"
    frame_aspect = payload.get("frameAspect") or "16:9"
    style = payload.get("style") or "电影写实风格，真实摄影质感，高质量影视概念设计"
    character = payload.get("character") or "根据剧本统一设计角色，但同一角色的五官、发型、服装、体型、年龄和气质必须保持一致。"
    scene = payload.get("scene") or "根据剧本统一设计场景，但建筑结构、空间方向、光源方向、材质和氛围必须保持一致。"
    layout = payload.get("layout") or "严格使用专业 MV 分镜故事板版式。"
    refs = collect_refs(payload.get("refs", []))
    story_brief = "；".join(f"{shot['cut']}（{shot['time']}）：{shot['action']}" for shot in group)
    if frame_aspect == "9:16":
        frame_layout = (
            "分镜画面比例固定为 9:16。每个小分镜必须是竖向画面，不得拉伸、裁歪或变成横图；"
            "主分镜区重新排版为 Cut 卡片单元；每个 Cut 单元内部必须左 50% 为 9:16 竖向分镜画面区，右 50% 为白底文字信息区，"
            "左右两区等宽，文字区不得侵占、覆盖或压缩画面主体。"
        )
    else:
        frame_layout = (
            "16:9 版式必须严格参考用户提供的“版式1.png”布局：顶部左侧大标题，右上角总时长/组号；标题下方一条红色版式提示栏；"
            "中部为 5 条横向 Cut 行；每条 Cut 行左侧 50% 是 16:9 分镜画面框，右侧 50% 是白底文字信息栏；"
            "下方为两栏“俯视场景图 / 关键空间关系”；底部为三栏“灯光示意图 / 色彩参考 / 氛围关键词”；最底部可放一行红色版式注释。"
            "分镜画面比例固定为精准 16:9。这里的 16:9 指每个 Cut 的画面框本身必须是标准横向矩形，"
            "宽高比例接近 1.777:1，例如 16 单位宽、9 单位高；绝对不能画成超宽长条、细长横幅、21:9、2.35:1 或超过 2:1 的比例。"
            "主分镜区使用横向 Cut 行排版；每个 Cut 行内部必须左 50% 为一个标准 16:9 画面框，右 50% 为白底文字信息区，"
            "左右两区等宽；文字区必须在画面框之外，不得侵占、覆盖、拉伸或压扁 16:9 分镜画面。所有 Cut 的 16:9 画面框必须完全等宽等高。"
            "每个 16:9 分镜画面框左上角必须有黑底白字 Cut 编号块；右侧文字信息栏必须左对齐，行距清楚，包含镜号、时序、景别、动作关键词、调度关键词、台词；有台词时台词可用红色强调。"
            "不要使用自由宫格、拼贴海报、漫画页、多列杂乱卡片或把 5 个 Cut 挤成细长横幅。"
            "如果版面过挤，优先减少单组分镜数量或增加画面框高度，不能把 16:9 画面压成过长横条。"
        )
    cuts = []
    for i, shot in enumerate(group, 1):
        cuts.append(
            f"""第 {i} 行：
左侧画面：{shot['cut']}，{shot['time']}，{shot['shotSize']}。{shot['description']}
右侧文字：
镜号：{shot['cut']}
时序：{shot['time']}
景别：{shot['shotSize']}
动作关键词：{shot['keyword']}
调度关键词：{shot['camera']} / {shot['functionName']}
台词：{shot['dialogue']}"""
        )

    return f"""生成一张用于影片制作的专业分镜故事板图片，画幅比例 {ratio}，{style}。

故事板 Agent 规则来源：
本提示词由本地 storyboard_agent_server.py 读取 AGENTS.md 后生成，遵守其中的视频生产型分镜故事板、角色连续性、场景连续性、导演调度、版式可读性和清晰度约束。

故事板内容：
{story_brief}

参考图使用：
{refs}

人物与场景设定：
角色设定：{character}
场景设定：{scene}

版式锁定：
{layout}

分镜画面尺寸：
{frame_layout}

16:9 版式参考：
当分镜画面比例选择 16:9 时，必须按照“版式1.png”的布局逻辑执行：标题区、红色提示栏、5 条 Cut 横向行、每行左半区 16:9 分镜框、右半区文字信息栏、下方两栏空间图、底部三栏灯光/色彩/氛围。此布局为硬性参考，不得改成海报式拼贴或自由宫格。

顶部标题：
主标题：{title}
副标题：总时长 {duration} / 第 {group_index + 1} 组

整体要求：
这是一张完整的视频生产型分镜故事板，不是单张电影海报，也不是纯文字表格。画面必须同时包含主分镜板、场景图、光影与氛围三个模块。所有分镜必须保持同一角色、同一场景、同一道具、同一光影方向和同一色调体系的连续性。动作从前一镜自然延续到后一镜，镜头方向清楚，不要跳轴。必须符合导演调度和剪辑语法：先建立空间关系，再推进动作和情绪；遵守 180 度轴线规则、视线匹配、运动方向连续、动作匹配剪辑；每个镜头必须有明确叙事功能和运镜动机。

--- 分镜板（主模块）---
严格使用 {len(group)} 个 Cut 单元。每个 Cut 单元必须采用左右 50/50 分栏：左侧 50% 是分镜画面区，只放该 Cut 画面；右侧 50% 是白底文字信息区，只放文字。人物台词必须放在右侧文字信息区展示，不能写在分镜画面内部，不能遮挡人物脸部、手部、关键动作和重要道具。右侧文字区必须包含镜号、时序、景别、动作关键词、调度关键词、台词；如无台词写“台词：无”。每个小分镜画面必须严格保持 {frame_aspect} 比例，这是画面框本身的硬性尺寸，不是内容裁切建议。所有分镜画面尺寸一致，不能出现忽宽忽窄、忽横忽竖、比例变形、画面互相重叠。{frame_layout}

{chr(10).join(cuts)}

--- 场景图（Secondary）---
位置：分镜板下方，生成 2 张空间参考图。
1. 俯视场景图：展示主要空间布局、角色起点、动作推进方向、关键道具位置、最终定格位置，只使用短标签和箭头。
2. 关键空间关系：展示场景纵深、入口、背景结构、主机位方向、光源位置和轴线关系，继承参考图或剧本中的核心环境。

--- 光影与氛围（Lighting & Mood）---
位置：画面底部三栏排列。
灯光示意图：主光、环境光、轮廓光、特殊光源方向。
色彩参考：3-6 个主要色块，来自角色服装、场景主色和关键光源。
氛围关键词：3-6 个关键词，准确表达本组镜头情绪。

清晰度与降噪：
clean image, low noise, minimal grain, clean shadows, simplified background texture, sharp subject, readable layout, no dirty noise, no compression artifacts. 暗部保留层次但不要脏黑；背景减少高频纹理；每个分镜只保留 1-2 个视觉重点；人物脸部、手部、关键道具、分镜边框和文字区域必须优先清晰。

避免：
不要自由排版；不要生成单张电影海报；不要生成纯文字表格；不要生成漫画风格，除非明确要求；不要出现多余角色；不要让同一角色变成不同人；不要出现重复脸、错乱五官、畸形手、错乱文字；不要让分镜格互相重叠；不要让文字遮挡关键画面；不要改变参考图中的核心人物和核心场景；不要强胶片颗粒、脏噪点、低清压缩伪影、过量烟雾、暗部糊成一片、背景满屏细碎纹理、过度锐化、过度运动模糊。
"""


def build_video_prompt(payload, group):
    duration = payload.get("duration") or "15s"
    style = payload.get("style") or "电影写实风格，真实摄影质感，高质量 MV / 短片镜头"
    character = payload.get("character") or "保持故事板中同一角色的五官、发型、服装、体型、年龄和气质一致。"
    scene = payload.get("scene") or "保持故事板中同一场景的建筑结构、空间方向、材质、道具和光源方向一致。"
    refs = collect_refs(payload.get("refs", []))
    lines = "\n".join(
        f"{shot['time']}：{shot['shotSize']}，{shot['angle']}，{shot['camera']}。{shot['action']}。{shot['blocking']}"
        for shot in group
    )
    return f"""根据当前分镜故事板图片，生成一段电影写实视频。参考图和故事板中的人物、场景、服装、道具、光影、色调必须保持一致。

视频时长：{duration}
本组镜头：{group[0]['cut']} 至 {group[-1]['cut']}
风格：{style}

参考图使用：
{refs}

人物与场景：
角色设定：{character}
场景设定：{scene}

镜头时间线：
{lines}

视频连续性：
动作必须从上一镜自然延续到下一镜；保持 180 度轴线、视线匹配、运动方向连续和动作匹配剪辑；不要无故跳轴；不要让角色位置、手部、头部、身体朝向、道具位置在相邻镜头中突然改变。重要动作必须有起因、过程和结果，重要情绪用近景或特写强化。

镜头语言：
先建立空间关系，再推进动作和情绪。每一次运镜都必须有明确动机：推进用于靠近人物情绪或发现关键动作，横移用于跟随行动，固定镜头用于压迫、冷静观察或定格。景别要有变化，不要连续使用几乎相同的角度和景别。

画质与光影：
cinematic realism, smooth camera motion, natural motion, sharp face, sharp hands, clean image, low noise, minimal grain, clean shadows, no dirty noise, no compression artifacts. 光影、色彩和氛围继承故事板，暗部保留层次，背景细节不要抢主体。

避免：
不要换脸；不要换服装；不要改变发型；不要改变场景结构；不要出现多余角色；不要错乱五官；不要畸形手；不要镜头乱跳；不要过度运动模糊；不要低清压缩伪影；不要文字水印。"""


def generate_payload(payload):
    agent_rules = read_agent_rules()
    group_size = int(payload.get("groupSize") or 5)
    llm_result = None
    llm_error = ""
    if api_is_enabled(payload):
        try:
            llm_result = llm_analyze_script(payload, include_parts=True)
        except Exception as exc:
            llm_error = f"{type(exc).__name__}: {exc}"

    # 检查是否有参考图
    refs = payload.get("refs", [])
    has_refs = any(ref.get("name") != "未上传" for ref in refs if isinstance(ref, dict))

    inferred_character = (
        payload.get("character")
        or (llm_result or {}).get("character")
        or infer_character_setting(payload.get("script", ""), has_refs=has_refs)
    )
    inferred_scene = (
        payload.get("scene")
        or (llm_result or {}).get("scene")
        or infer_scene_setting(payload.get("script", ""), has_refs=has_refs)
    )
    enriched_payload = dict(payload)
    enriched_payload["character"] = inferred_character
    enriched_payload["scene"] = inferred_scene
    if isinstance((llm_result or {}).get("parts"), list):
        enriched_payload["_shotParts"] = llm_result["parts"]
    shots = build_shots(enriched_payload)
    groups = chunk_shots(shots, group_size)
    prompt_groups = []
    for index, group in enumerate(groups):
        prompt_groups.append(
            {
                "label": f"第 {index + 1} 组：{group[0]['cut']}-{group[-1]['cut']}",
                "imagePrompt": build_storyboard_prompt(enriched_payload, group, index, agent_rules),
                "videoPrompt": build_video_prompt(enriched_payload, group),
            }
        )
    return {
        "backend": "storyboard-agent",
        "agentSource": str(AGENT_PATH),
        "usedLLM": bool(llm_result),
        "llmError": llm_error,
        "inferredCharacter": inferred_character,
        "inferredScene": inferred_scene,
        "shots": shots,
        "groups": prompt_groups,
    }


def generate_extract_payload(payload):
    script = payload.get("script", "")
    llm_result = None
    llm_error = ""
    if api_is_enabled(payload):
        try:
            llm_result = llm_analyze_script(payload, include_parts=False)
        except Exception as exc:
            llm_error = f"{type(exc).__name__}: {exc}"

    # 检查是否有参考图
    refs = payload.get("refs", [])
    has_refs = any(ref.get("name") != "未上传" for ref in refs if isinstance(ref, dict))

    return {
        "backend": "storyboard-agent",
        "agentSource": str(AGENT_PATH),
        "usedLLM": bool(llm_result),
        "llmError": llm_error,
        "inferredCharacter": (llm_result or {}).get("character") or infer_character_setting(script, has_refs=has_refs),
        "inferredScene": (llm_result or {}).get("scene") or infer_scene_setting(script, has_refs=has_refs),
    }


class Handler(BaseHTTPRequestHandler):
    def _headers(self, status=200, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", os.getenv("CORS_ORIGIN", "*"))
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._headers(204)

    def do_GET(self):
        if self.path in {"/", "/storyboard-workflow.html"}:
            if not HTML_PATH.exists():
                self._headers(404)
                self.wfile.write(json.dumps({"error": "storyboard-workflow.html not found"}, ensure_ascii=False).encode("utf-8"))
                return
            self._headers(200, "text/html; charset=utf-8")
            self.wfile.write(HTML_PATH.read_bytes())
            return
        if self.path == "/health":
            self._headers(200)
            self.wfile.write(json.dumps({"ok": True, "service": "storyboard-agent"}, ensure_ascii=False).encode("utf-8"))
            return
        self._headers(404)
        self.wfile.write(json.dumps({"error": "not found"}, ensure_ascii=False).encode("utf-8"))

    def do_POST(self):
        if self.path not in {"/agent/storyboard", "/agent/extract"}:
            self._headers(404)
            self.wfile.write(json.dumps({"error": "not found"}, ensure_ascii=False).encode("utf-8"))
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if self.path == "/agent/extract":
                result = generate_extract_payload(payload)
            else:
                result = generate_payload(payload)
            self._headers(200)
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
        except Exception as exc:
            self._headers(500)
            self.wfile.write(json.dumps({"error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False).encode("utf-8"))

    def log_message(self, fmt, *args):
        return


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Storyboard Agent running at http://{HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
