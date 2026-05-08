import requests, os
from dotenv import load_dotenv
load_dotenv()
r = requests.get(os.getenv("OPENAI_BASE_URL")+"/models",
                 headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"})
data = r.json()["data"]
img = [m for m in data if "image-generation" in m.get("supported_endpoint_types", []) or "image" in m["id"].lower() or "dall" in m["id"].lower()]
for m in img:
    print(m["id"], "->", m.get("supported_endpoint_types"))
