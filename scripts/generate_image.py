"""Gera uma imagem a partir de um prompt usando a API de imagens da OpenAI."""
import argparse
import base64
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = "https://api.openai.com/v1/images/generations"
SIZES = {"square": "1024x1024", "portrait": "1024x1536", "landscape": "1536x1024"}
# Guarda a ultima cena sorteada para nao repetir a mesma no post seguinte.
# Precisa ser commitado junto com a imagem: cada execucao agendada roda num
# container novo, entao so o que estiver no git persiste entre posts.
LAST_SCENE_FILE = Path(__file__).resolve().parent.parent / "assets" / "posts" / ".last_scene"


def generate(prompt: str, out_path: str, size: str, quality: str):
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "gpt-image-1",
            "prompt": prompt,
            "size": SIZES.get(size, size),
            "quality": quality,
            "n": 1,
        },
        timeout=180,
    )
    result = resp.json()
    if "data" not in result:
        raise RuntimeError(f"Erro ao gerar imagem: {result}")

    image_bytes = base64.b64decode(result["data"][0]["b64_json"])
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(image_bytes)
    print(f"Imagem gerada: {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera uma imagem via API da OpenAI (gpt-image-1).")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt", help="Descrição da imagem a gerar.")
    src.add_argument("--prompt-file", help="Arquivo de texto com o prompt (alternativa a --prompt).")
    src.add_argument("--random-scene", action="store_true",
                      help="Sorteia o assunto do post (impressora, peça pronta, filamento etc.)"
                           " em vez de usar um prompt fixo — ver scripts/scenes.py.")
    parser.add_argument("--out", required=True, help="Caminho do arquivo PNG de saída.")
    parser.add_argument("--size", default="square", choices=list(SIZES) + list(SIZES.values()),
                         help="square (1024x1024, padrão), portrait (1024x1536) ou landscape (1536x1024).")
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high"])
    args = parser.parse_args()

    if not API_KEY:
        print("ERRO: OPENAI_API_KEY nao encontrada. Defina no .env ou como variavel de ambiente.")
        sys.exit(1)

    if args.random_scene:
        from scenes import pick_random_prompt
        last_scene = LAST_SCENE_FILE.read_text().strip() if LAST_SCENE_FILE.exists() else None
        scene_name, prompt = pick_random_prompt(exclude=last_scene)
        LAST_SCENE_FILE.parent.mkdir(parents=True, exist_ok=True)
        LAST_SCENE_FILE.write_text(scene_name + "\n")
        print(f"Cena sorteada: {scene_name}" + (f" (anterior: {last_scene})" if last_scene else ""))
    else:
        prompt = args.prompt or Path(args.prompt_file).read_text(encoding="utf-8").strip()

    generate(prompt, args.out, args.size, args.quality)
