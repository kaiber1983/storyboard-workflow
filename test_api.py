"""连通性测试：验证 API Key / Base URL / 模型名 三者是否都通。"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("IMAGE_MODEL", "gpt-image-2")

print(f"[config] base_url = {base_url}")
print(f"[config] model    = {model}")
print(f"[config] key      = {api_key[:10]}...{api_key[-4:]}")

client = OpenAI(api_key=api_key, base_url=base_url)

try:
    resp = client.images.generate(
        model=model,
        prompt="a red apple on a white table, minimal",
        size="1024x1024",
        n=1,
    )
    item = resp.data[0]
    if getattr(item, "url", None):
        print(f"[ok] url = {item.url}")
    elif getattr(item, "b64_json", None):
        print(f"[ok] got b64_json, length = {len(item.b64_json)}")
    else:
        print(f"[warn] unknown response shape: {item}")
except Exception as e:
    print(f"[error] {type(e).__name__}: {e}")
