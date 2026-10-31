"""Gera a imagem de um post de impressão 3D usando a API de imagens da OpenAI.

Uso típico (sorteia a cena, evitando repetir a do post anterior):

    python3 scripts/generate_image.py --random-scene \
        --out assets/posts/3d-printing-2026-10-31.png --quality high

A cena sorteada é registrada em assets/posts/.last_scene para que a próxima
execução não repita a mesma cena. Esse arquivo precisa ser commitado, porque
cada execução agendada começa num container novo.
"""
import argparse
import base64
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv

from scenes import SCENES, SCENES_BY_KEY, build_prompt

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

LAST_SCENE_FILE = Path(__file__).resolve().parent.parent / "assets" / "posts" / ".last_scene"
MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2")


def read_last_scene() -> str | None:
    try:
        value = LAST_SCENE_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    return value or None


def write_last_scene(key: str) -> None:
    LAST_SCENE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_SCENE_FILE.write_text(key + "\n", encoding="utf-8")


def pick_scene(explicit_key: str | None, avoid_repeat: bool) -> dict:
    if explicit_key:
        if explicit_key not in SCENES_BY_KEY:
            print(f"ERRO: cena desconhecida '{explicit_key}'.")
            print("Cenas disponiveis: " + ", ".join(SCENES_BY_KEY))
            sys.exit(1)
        return SCENES_BY_KEY[explicit_key]

    candidates = list(SCENES)
    last = read_last_scene() if avoid_repeat else None
    if last:
        filtered = [s for s in candidates if s["key"] != last]
        if filtered:
            candidates = filtered
            print(f"  (evitando repetir a cena anterior: {last})")
    return random.choice(candidates)


def generate(scene: dict, out_path: Path, quality: str, size: str) -> None:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERRO: OPENAI_API_KEY nao encontrada no ambiente (nem no .env).")
        sys.exit(1)

    prompt = build_prompt(scene)
    print(f"\nGerando imagem com {MODEL} (quality={quality}, size={size})...")
    client = OpenAI(api_key=api_key)
    result = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
    )

    data = result.data[0]
    if getattr(data, "b64_json", None):
        raw = base64.b64decode(data.b64_json)
    else:
        import requests

        raw = requests.get(data.url, timeout=120).content

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(raw)
    print(f"Imagem salva em {out_path} ({len(raw) / 1024:.0f} KB)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera a imagem de um post de impressao 3D.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--random-scene", action="store_true",
                       help="Sorteia uma cena, evitando repetir a do post anterior.")
    group.add_argument("--scene", help="Usa uma cena especifica (chave de scenes.py).")
    parser.add_argument("--out", required=True, help="Caminho do PNG de saida.")
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high"],
                        help="Qualidade da imagem (use 'high' para publicar).")
    parser.add_argument("--size", default="1024x1024", help="Dimensoes da imagem (padrao 1024x1024).")
    parser.add_argument("--list-scenes", action="store_true", help="Lista as cenas e sai.")
    parser.add_argument("--no-save-scene", action="store_true",
                        help="Nao atualiza o arquivo .last_scene.")
    args = parser.parse_args()

    if args.list_scenes:
        for s in SCENES:
            print(f"{s['key']:22s} {s['label']}")
        return

    scene = pick_scene(args.scene, avoid_repeat=args.random_scene)
    print(f"\nCena sorteada: {scene['label']} ({scene['key']})")

    generate(scene, Path(args.out), args.quality, args.size)

    if not args.no_save_scene:
        write_last_scene(scene["key"])
        print(f"Cena registrada em {LAST_SCENE_FILE.name} para evitar repeticao no proximo post.")


if __name__ == "__main__":
    main()
