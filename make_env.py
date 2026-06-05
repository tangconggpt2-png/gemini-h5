import pathlib
import re

src = pathlib.Path(r"C:\Users\tangc_gmk\Downloads\gemini-h5\gemini-h5-export\opt_gemini-h5\backend\main.py")
text = src.read_text(encoding="utf-8")
m = re.search(r'API_TOKEN = os\.environ\.get\("AI_TOKEN", "([^"]+)"\)', text)
token = m.group(1) if m else ""
out = pathlib.Path(__file__).with_name(".env")
out.write_text(
    "AI_BASE_URL=https://yinli.one/\n"
    f"AI_TOKEN={token}\n"
    "AI_MODEL=gemini-3.1-pro-preview\n"
    "CHAT_LOG_FILE=/opt/gemini-h5/backend/chat.log\n"
    "FRP_TOKEN=030438\n"
    "FRP_SERVER_ADDR=frp4.ccszxc.xin\n"
    "FRP_SERVER_PORT=55722\n"
    "FRP_REMOTE_PORT=55730\n",
    encoding="utf-8",
)
print("wrote", out, "token_len=", len(token))
