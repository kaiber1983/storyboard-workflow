"""批量生成 10 张不同姿势+服装的性感时尚大片。串行执行，失败跳过。"""
import os
import sys
import time
import base64
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SHOTS = [
    ("poolside",       "Fashion editorial photograph of a gorgeous east asian female model with porcelain fair flawless skin, age 26, reclining on the edge of an infinity pool, back arched, head tilted back with wet glossy long hair dripping, one arm propping her up, wearing a high-cut one-piece black swimsuit, long toned legs, glistening water droplets on skin, turquoise pool water, golden hour sunlight, shot on Hasselblad 85mm, Vogue swimwear editorial, photorealistic, 8k, no text, no watermark, no logo"),
    ("bathtub",        "Fashion editorial photograph of a gorgeous east asian female model with porcelain fair flawless skin, age 26, leaning back against the edge of a luxury marble bathtub, one knee raised above the foam, arm draped elegantly along the rim, wearing a white silk slip nightgown with thin straps, wet hair slicked back, dewy skin, candlelight and warm ambient glow, marble bathroom with gold fixtures, shot on Canon 50mm f1.2, magazine editorial, photorealistic, 8k, no text, no watermark, no logo"),
    ("velvet_sofa",    "Fashion editorial photograph of a gorgeous east asian female model with porcelain fair flawless skin, age 26, seated sideways on a deep red velvet vintage sofa, long legs crossed and stretched out, wearing a wine-red satin gown with plunging V-neck and high thigh slit, looking over her bare shoulder at the camera, glossy wavy long hair, diamond choker, moody chiaroscuro lighting, dark emerald curtain background, shot on Hasselblad 85mm f1.4, Vogue cover aesthetic, photorealistic, 8k, no text, no watermark, no logo"),
    ("beach_sunset",   "Fashion editorial photograph of a gorgeous east asian female model with porcelain fair flawless skin, age 26, walking toward the ocean at sunset, turning back mid-step tossing her wet hair, wearing a cream white bikini with a sheer chiffon sarong wrapped around her hips billowing in the wind, silhouette rim light, golden orange sky, tropical beach, shot on Sony GM 35mm, swimwear campaign, photorealistic, 8k, no text, no watermark, no logo"),
    ("loft_wall",      "Fashion editorial photograph of a gorgeous east asian female model with porcelain fair flawless skin, age 26, leaning against a rough concrete loft wall, one knee bent with foot flat on the wall, hands running through her hair, wearing tight black leather pants and a white silk shirt half-unbuttoned revealing a hint of collarbone and a lace bralette, smokey eye makeup, industrial window with harsh sunbeam, shot on Leica 50mm Summilux, fashion campaign, photorealistic, 8k, no text, no watermark, no logo"),
    ("neon_rain",      "Fashion editorial photograph of a gorgeous east asian female model with porcelain fair flawless skin, age 26, standing in a rainy neon-lit Tokyo alley at night, half turning back over her shoulder, wet hair clinging to her face, wearing a black sheer lace long-sleeve top over a black bralette and a tight leather mini skirt, stockings, wet glossy skin reflecting pink and cyan neon signs, cinematic cyberpunk mood, shot on Sony 35mm f1.4, photorealistic, 8k, no text, no watermark, no logo"),
    ("wheat_field",    "Fashion editorial photograph of a gorgeous east asian female model with porcelain fair flawless skin, age 26, spinning joyfully in a golden wheat field at sunset, white off-shoulder flowing maxi dress billowing in the wind revealing bare shoulders and long legs, long hair flying, laughing, warm golden hour backlight and lens flare, shot on Canon RF 85mm f1.2, romantic fashion campaign, photorealistic, 8k, no text, no watermark, no logo"),
    ("gym",            "Fashion editorial photograph of a gorgeous east asian female model with porcelain fair flawless skin, age 26, in a high-end gym, low crouch pose on one knee with elbow resting on raised knee, wiping sweat with a towel, wearing a fitted black sports bra and high-waisted seamless leggings, toned athletic abs and long legs, hair in a sleek ponytail, dewy sweat-glistened skin, moody side lighting, shot on Canon 50mm f1.2, activewear campaign, photorealistic, 8k, no text, no watermark, no logo"),
    ("castle_library", "Fashion editorial photograph of a gorgeous east asian female model with porcelain fair flawless skin, age 26, seated in a tall antique leather armchair in a gothic castle library, one long leg crossed over the other, chin resting on her hand, wearing a black belted leather trench coat over a black slip dress with high thigh slit, tall black over-the-knee leather boots, glossy long hair, fireplace warm light, bookshelves background, shot on Hasselblad 85mm, dark luxury editorial, photorealistic, 8k, no text, no watermark, no logo"),
    ("hot_spring",     "Fashion editorial photograph of a gorgeous east asian female model with porcelain fair flawless skin, age 26, lying face down on the edge of a snowy mountain hot spring, arms folded supporting her chin, looking back with a soft smile, smooth bare back shown above water with a strapless bandeau swimsuit, wet hair, steam rising from the hot spring, snow-capped mountains background, shot on Sony GM 85mm, travel luxury campaign, photorealistic, 8k, no text, no watermark, no logo"),
]

SIZE = "1024x1536"
MODEL = os.getenv("IMAGE_MODEL", "gpt-image-2")
OUT = Path("./output")
OUT.mkdir(exist_ok=True)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
log = []

for idx, (tag, prompt) in enumerate(SHOTS, 1):
    name = f"sexy10_{idx:02d}_{tag}_{ts}.png"
    path = OUT / name
    print(f"\n[{idx}/10] {tag} -> {name}")
    t0 = time.time()
    try:
        resp = client.images.generate(
            model=MODEL, prompt=prompt, size=SIZE, n=1,
        )
        item = resp.data[0]
        if getattr(item, "b64_json", None):
            path.write_bytes(base64.b64decode(item.b64_json))
        elif getattr(item, "url", None):
            r = requests.get(item.url, timeout=120)
            r.raise_for_status()
            path.write_bytes(r.content)
        else:
            raise RuntimeError(f"empty response: {item}")
        dt = time.time() - t0
        print(f"  [ok] saved in {dt:.1f}s -> {path}")
        log.append((idx, tag, "ok", name))
    except Exception as e:
        dt = time.time() - t0
        msg = f"{type(e).__name__}: {str(e)[:200]}"
        print(f"  [fail] {dt:.1f}s {msg}")
        log.append((idx, tag, "fail", msg))

print("\n========= SUMMARY =========")
for i, tag, status, info in log:
    print(f"  {i:02d} {tag:15s} {status:4s} {info}")
ok = sum(1 for _, _, s, _ in log if s == "ok")
print(f"\nTotal: {ok}/10 succeeded")
