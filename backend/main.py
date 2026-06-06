# -*- coding: utf-8 -*-

import os
import json
import ssl
import datetime
import urllib.request
import urllib.error

from flask import Flask, request, jsonify

app = Flask(__name__)

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.environ.get(
    "PROMPT_CONFIG_DIR", os.path.join(BACKEND_DIR, "config")
)
EXAMPLES_DIR = os.environ.get(
    "PROMPT_EXAMPLES_DIR", os.path.join(BACKEND_DIR, "examples")
)
DEFAULTS_DIR = os.environ.get("GEMINI_DEFAULTS_DIR", "/opt/gemini-h5/defaults")


def resolve_config_path(filename):
    if filename == "ai.config" and os.environ.get("AI_CONFIG_FILE"):
        return os.environ["AI_CONFIG_FILE"]
    if filename == "system_prompt.txt" and os.environ.get("SYSTEM_PROMPT_FILE"):
        return os.environ["SYSTEM_PROMPT_FILE"]
    if filename == "active_examples.txt" and os.environ.get("ACTIVE_EXAMPLES_FILE"):
        return os.environ["ACTIVE_EXAMPLES_FILE"]

    primary = os.path.join(CONFIG_DIR, filename)
    if os.path.isfile(primary):
        return primary

    fallback = os.path.join(DEFAULTS_DIR, "config", filename)
    if os.path.isfile(fallback):
        return fallback

    return primary


def resolve_example_path(name):
    safe_name = os.path.basename(name)
    primary = os.path.join(EXAMPLES_DIR, safe_name)
    if os.path.isfile(primary):
        return primary

    fallback = os.path.join(DEFAULTS_DIR, "examples", safe_name)
    if os.path.isfile(fallback):
        return fallback

    return primary


def read_key_value_file(path):
    """读取 KEY=VALUE 配置文件，返回字典。"""
    values = {}
    if not path or not os.path.isfile(path):
        return values
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, value = line.partition("=")
            if sep:
                values[key.strip()] = value.strip()
    return values


def load_ai_settings():
    """每次请求读取 API 配置；优先外部挂载，否则回退镜像内置 defaults。"""
    values = read_key_value_file(resolve_config_path("ai.config"))
    return {
        "base_url": values.get("AI_BASE_URL", "").rstrip("/"),
        "token": values.get("AI_TOKEN", ""),
        "model": values.get("AI_MODEL", "gemini-3.1-pro-preview"),
    }


LOG_FILE_BASE = os.environ.get(
    "CHAT_LOG_FILE", os.path.join(BACKEND_DIR, "data", "chat.log")
)


def resolve_log_file(when=None):
    """按日期分文件，如 data/chat.log.20260606。"""
    when = when or datetime.datetime.now()
    log_dir = os.path.dirname(LOG_FILE_BASE) or "."
    base_name = os.path.basename(LOG_FILE_BASE) or "chat.log"
    return os.path.join(log_dir, base_name + "." + when.strftime("%Y%m%d"))

DEFAULT_SYSTEM_PROMPT = (
    "请出于让视频火爆的角度修改文案。"
    "保持用户原文的核心信息，优化标题与正文，使其更适合短视频传播。"
)


def read_text_file(path, default=""):
    if not path or not os.path.isfile(path):
        return default
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def load_system_prompt():
    text = read_text_file(resolve_config_path("system_prompt.txt"), "")
    return text if text else DEFAULT_SYSTEM_PROMPT


def load_active_example_names():
    """读取 config/active_examples.txt，每行一个示例文件名。"""
    raw = read_text_file(resolve_config_path("active_examples.txt"), "")
    names = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # 支持一行里写多个：案例1.txt,案例2.txt
        for part in line.split(","):
            name = part.strip()
            if name:
                names.append(name)
    return names


def load_examples_block():
    names = load_active_example_names()
    if not names:
        return ""

    blocks = [
        "以下是「修改前 / 修改后」参考示例，请学习其风格与改写方式：",
        "",
    ]
    loaded = 0
    for name in names:
        safe_name = os.path.basename(name)
        path = resolve_example_path(safe_name)
        if not os.path.isfile(path):
            blocks.append(f"（示例文件不存在，已跳过：{safe_name}）")
            blocks.append("")
            continue
        content = read_text_file(path)
        if not content:
            continue
        blocks.append(f"--- 示例：{safe_name} ---")
        blocks.append(content)
        blocks.append("")
        loaded += 1

    if loaded == 0:
        return ""

    blocks.append(
        "请参照以上示例，处理用户随后提供的待改文案。"
        "只输出修改后的完整文案，不要解释过程。"
    )
    return "\n".join(blocks)


def build_chat_messages(user_message):
    """组装发给 AI 的消息：system 含提示词与示例，user 仅为用户文案。"""
    system_parts = [load_system_prompt()]
    examples = load_examples_block()
    if examples:
        system_parts.append(examples)

    system_content = "\n\n".join(part for part in system_parts if part.strip())
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_message.strip()},
    ]


def now_text():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_messages_for_log(messages):
    """将发给 AI 的 messages 整理成可读文本。"""
    parts = []
    for item in messages:
        role = item.get("role", "unknown")
        content = (item.get("content") or "").strip()
        parts.append(f"--- {role} ---")
        parts.append(content if content else "（空）")
        parts.append("")
    return "\n".join(parts).strip()


def append_log(user_message, ai_reply, messages=None, error=None):
    """追加一条可读对话记录（按天写入独立文件）。"""
    log_file = resolve_log_file()
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    lines = [
        "",
        "=" * 20 + " " + now_text() + " " + "=" * 20,
        "",
        "【用户输入】",
        user_message.strip() if user_message else "（空）",
        "",
    ]

    if messages:
        lines.extend([
            "【当时完整 Prompt】",
            format_messages_for_log(messages),
            "",
        ])

    if error:
        lines.extend([
            "【AI 回复】",
            "（请求失败，无回复）",
            "",
            "【错误信息】",
            error.strip(),
        ])
    else:
        lines.extend([
            "【AI 回复】",
            (ai_reply or "（空）").strip(),
        ])

    lines.append("")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write("\n".join(lines))


def call_ai(messages, ai_settings):
    if not ai_settings["base_url"]:
        raise ValueError("未配置 AI_BASE_URL，请检查 config/ai.config。")

    url = ai_settings["base_url"] + "/v1/chat/completions"

    payload = {
        "model": ai_settings["model"],
        "messages": messages,
        "temperature": 0.7,
        "stream": False,
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url=url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + ai_settings["token"],
        },
        method="POST",
    )

    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=300, context=ctx) as resp:
        body = resp.read().decode("utf-8")
        result = json.loads(body)

    return result["choices"][0]["message"]["content"]


@app.route("/api/chat", methods=["POST"])
def chat():
    ai_settings = load_ai_settings()

    if not ai_settings["token"]:
        return jsonify({
            "reply": "后端没有设置 AI_TOKEN，请编辑 config/ai.config。"
        }), 500

    data = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "reply": "请输入问题。"
        }), 400

    messages = build_chat_messages(user_message)

    try:
        ai_reply = call_ai(messages, ai_settings)
        append_log(user_message=user_message, ai_reply=ai_reply, messages=messages)
        return jsonify({
            "reply": ai_reply,
            "model": ai_settings["model"],
        })

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        error_text = "AI 接口请求失败，状态码：" + str(e.code) + "，返回：" + error_body
        append_log(
            user_message=user_message,
            ai_reply="",
            messages=messages,
            error=error_text,
        )
        return jsonify({
            "reply": "AI 接口请求失败，状态码：" + str(e.code),
            "detail": error_body,
        }), 500

    except Exception as e:
        error_text = str(e)
        append_log(
            user_message=user_message,
            ai_reply="",
            messages=messages,
            error=error_text,
        )
        return jsonify({
            "reply": "后端请求 AI 接口异常：" + error_text
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
