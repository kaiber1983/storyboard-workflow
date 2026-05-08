"""I2V 图生图脚本：基于参考图改场景，保持人物面部一致性。

用法：
    python i2v.py "参考图路径" "新场景描述" [--out ./output] [--size 1536x1024]

原理：
    调用 OpenAI Images Edit API (inpainting)，
    将原图作为 image 输入，prompt 描述期望的新场景，
    模型在保留人物特征的前提下变换背景/服装/动作。
"""
import argparse
import base64
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

COUNTER_FILE = ".counter"


def get_next_number(out_dir: Path) -> int:
    cp = out_dir / COUNTER_FILE
    n = 1
    if cp.exists():
        n = int(cp.read_text().strip()) + 1
    cp.write_text(str(n))
    return n


def main():
    ap = argparse.ArgumentParser(description="I2V: 基于参考图生成新场景图片，保持人物一致性")
    ap.add_argument("image", help="参考图片路径")
    ap.add_argument("prompt", help="新场景描述 prompt")
    ap.add_argument("--size", default="1536x1024", help="尺寸，默认 1536x1024 (16:9)")
    ap.add_argument("--out", default="./output", help="输出目录")
    args = ap.parse_args()

    img_path = Path(args.image)
    if not img_path.exists():
        print(f"[error] 图片不存在: {img_path}")
        sys.exit(1)

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )
    model = os.getenv("IMAGE_MODEL", "gpt-image-2")

    print(f"[i2v] model={model} size={args.size}")
    print(f"[i2v] reference={img_path.name}")
    print(f"[i2v] prompt={args.prompt}")

    t0 = time.time()
    resp = client.images.edit(
        model=model,
        image=img_path.open("rb"),
        prompt=args.prompt,
        size=args.size,
        n=1,
    )

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    num = get_next_number(out_dir)
    fname = f"{num}.png"
    path = out_dir / fname

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
    print(f"[saved] {path} ({dt:.1f}s)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[error] {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
