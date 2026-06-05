# -*- coding: utf-8 -*-

import json
import urllib.request
import urllib.error

# 这里填你的 token
API_TOKEN = "sk-DpBiKUSy7uHui7ckbOwdQq6H3e03gsgLsmJ0yK4CWSZjWxqE"

# 这里填 Chatbox 里使用的模型名
# 例如：gpt-4o-mini / deepseek-chat / claude-xxx / 供应商给你的模型名
MODEL = "gemini-3.1-pro-preview"

# OpenAI 兼容接口地址
BASE_URL = "https://api.vectorengine.ai"

def main():
    url = BASE_URL.rstrip("/") + "/v1/chat/completions"

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "你好"
            }
        ],
        "temperature": 0.7,
        "stream": False
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url=url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + API_TOKEN
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            result = json.loads(body)

            print("HTTP 状态码:", resp.status)
            print("原始返回:")
            print(json.dumps(result, ensure_ascii=False, indent=2))

            try:
                answer = result["choices"][0]["message"]["content"]
                print("\n模型回复:")
                print(answer)
            except Exception:
                print("\n没有按 OpenAI chat completions 格式解析到回复。")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        print("HTTP 请求失败")
        print("状态码:", e.code)
        print("返回内容:")
        print(error_body)

    except Exception as e:
        print("请求异常:")
        print(str(e))


if __name__ == "__main__":
    main()
