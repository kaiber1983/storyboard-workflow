"""GPT-Image-2 出图脚本。

用法：
    python generate.py "提示词" [--size 1024x1024] [--n 1] [--out ./output]
"""
import argparse
import base64
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def slugify(text: str, max_len: int = 40) -> str:
    text = re.sub(r"[\s\W]+", "_", text, flags=re.UNICODE).strip("_")
    return text[:max_len] or "image"


def save_item(item, out_dir: Path, name: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    if getattr(item, "b64_json", None):
        path.write_bytes(base64.b64decode(item.b64_json))
    elif getattr(item, "url", None):
        r = requests.get(item.url, timeout=60)
        r.raise_for_status()
        path.write_bytes(r.content)
    else:
        raise RuntimeError(f"unknown response item: {item}")
    return path


COUNTER_FILE = ".counter"


def get_next_number(out_dir: Path) -> int:
    cp = out_dir / COUNTER_FILE
    n = 1
    if cp.exists():
        n = int(cp.read_text().strip()) + 1
    cp.write_text(str(n))
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", help="图片提示词")
    ap.add_argument("--size", default="1024x1024", help="默认 1024x1024")
    ap.add_argument("--n", type=int, default=1, help="生成张数")
    ap.add_argument("--out", default="./output", help="输出目录")
    ap.add_argument("--model", default=os.getenv("IMAGE_MODEL", "gpt-image-2"))
    args = ap.parse_args()

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )

    print(f"[generate] model={args.model} size={args.size} n={args.n}")
    print(f"[generate] prompt={args.prompt}")

    resp = client.images.generate(
        model=args.model,
        prompt=args.prompt,
        size=args.size,
        n=args.n,
    )

    out_dir = Path(args.out)

    for item in resp.data:
        num = get_next_number(out_dir)
        path = save_item(item, out_dir, f"{num}.png")
        print(f"[saved] {path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[error] {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
