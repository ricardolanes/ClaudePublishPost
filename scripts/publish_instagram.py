"""Publicação automática no Instagram via Meta Graph API."""
import argparse
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

IG_ID = os.getenv("INSTAGRAM_BUSINESS_ID")
PAGE_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
# Token type controls the API host: "IGAA..." tokens are Instagram Login tokens
# and only work against graph.instagram.com; "EAA..." tokens are Facebook Page
# tokens and use graph.facebook.com.
_HOST = "graph.instagram.com" if (PAGE_TOKEN or "").startswith("IGAA") else "graph.facebook.com"
BASE_URL = f"https://{_HOST}/{os.getenv('META_API_VERSION', 'v19.0')}"

# Aviso de transparencia: nesta automacao tanto a imagem quanto o texto sao
# gerados por IA, entao ele entra em toda legenda publicada pelo script.
AI_DISCLOSURE = "🤖 Post gerado por IA — imagem e texto criados com Claude Code."


def with_disclosure(caption: str) -> str:
    """Acrescenta o aviso de conteudo gerado por IA, antes do bloco final de hashtags."""
    caption = caption.strip()
    if AI_DISCLOSURE in caption:
        return caption
    blocks = caption.split("\n\n")
    if len(blocks) > 1 and blocks[-1].lstrip().startswith("#"):
        blocks.insert(-1, AI_DISCLOSURE)
    else:
        blocks.append(AI_DISCLOSURE)
    return "\n\n".join(blocks)


def host_image(image_path: str) -> str:
    """Hospeda a imagem em uma URL pública via catbox.moe (a Graph API exige uma URL, não um arquivo local)."""
    with open(image_path, "rb") as f:
        resp = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": (Path(image_path).name, f, "image/png")},
            timeout=60,
        )
    url = resp.text.strip()
    if not url.startswith("https://"):
        raise RuntimeError(
            f"Falha no upload da imagem via catbox.moe: {url}\n"
            "  catbox.moe costuma bloquear IPs de datacenter/proxy (comum em"
            " ambientes de nuvem). Alternativa: faça commit da imagem no"
            " repositorio e use a URL raw.githubusercontent.com como image_url"
            " diretamente na chamada da Graph API."
        )
    print(f"  Hospedada: {url}")
    return url


def create_media_container(image: str, caption: str, is_carousel_item: bool, is_url: bool = False) -> str:
    data = {"access_token": PAGE_TOKEN, "image_url": image if is_url else host_image(image)}
    if is_carousel_item:
        data["is_carousel_item"] = "true"
    else:
        data["caption"] = caption
    resp = requests.post(f"{BASE_URL}/{IG_ID}/media", data=data, timeout=60)
    result = resp.json()
    if "id" not in result:
        raise RuntimeError(f"Erro ao criar container: {result}")
    print(f"  Container: {result['id']}")
    return result["id"]


def create_carousel(media_ids: list, caption: str) -> str:
    resp = requests.post(f"{BASE_URL}/{IG_ID}/media", data={
        "access_token": PAGE_TOKEN,
        "media_type": "CAROUSEL",
        "children": ",".join(media_ids),
        "caption": caption,
    }, timeout=30)
    result = resp.json()
    if "id" not in result:
        raise RuntimeError(f"Erro ao criar carrossel: {result}")
    print(f"  Carrossel: {result['id']}")
    return result["id"]


def wait_ready(container_id: str) -> bool:
    for i in range(12):
        resp = requests.get(f"{BASE_URL}/{container_id}",
            params={"fields": "status_code", "access_token": PAGE_TOKEN}, timeout=15)
        status = resp.json().get("status_code", "")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            raise RuntimeError(f"Container com erro: {resp.json()}")
        print(f"  Processando... {i * 5}s")
        time.sleep(5)
    return False


def publish(container_id: str) -> str:
    resp = requests.post(f"{BASE_URL}/{IG_ID}/media_publish", data={
        "access_token": PAGE_TOKEN,
        "creation_id": container_id,
    }, timeout=30)
    result = resp.json()
    if "id" not in result:
        raise RuntimeError(f"Erro ao publicar: {result}")
    return result["id"]


def run(images: list, caption: str, dry_run: bool = False, is_url: bool = False):
    if not IG_ID or not PAGE_TOKEN:
        print("ERRO: credenciais nao encontradas. Preencha o arquivo .env na raiz do projeto"
              " (veja .env.example) antes de publicar.")
        sys.exit(1)
    if len(images) > 10:
        print("ERRO: maximo 10 imagens por post.")
        sys.exit(1)

    caption = with_disclosure(caption)
    is_carousel = len(images) > 1
    print(f"\nPublicando {len(images)} imagem(ns) no Instagram...")
    print(f"\nLegenda final:\n{caption}\n")
    if dry_run:
        print("[DRY RUN] Credenciais e imagens OK. Remova --dry-run para publicar de verdade.")
        return

    if is_carousel:
        print("\nPasso 1/3 - Criando containers do carrossel...")
        ids = [create_media_container(img, caption, True, is_url) for img in images]

        print("\nPasso 2/3 - Montando carrossel...")
        creation_id = create_carousel(ids, caption)
    else:
        print("\nPasso 1/2 - Criando container do post...")
        creation_id = create_media_container(images[0], caption, False, is_url)

    print(f"\nPasso {'3/3' if is_carousel else '2/2'} - Publicando...")
    if not wait_ready(creation_id):
        print("ERRO: timeout no processamento da imagem.")
        sys.exit(1)

    post_id = publish(creation_id)
    print("\nPublicado com sucesso!")
    print(f"Post ID: {post_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publica um post ou carrossel no Instagram via Meta Graph API.")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--images", nargs="+", help="Caminho de 1 a 10 imagens (PNG/JPG); sao hospedadas via catbox.moe.")
    src.add_argument("--image-urls", nargs="+", help="URLs publicas ja hospedadas (ex.: raw.githubusercontent.com),"
                     " usadas direto na Graph API — util quando o catbox.moe esta bloqueado.")
    parser.add_argument("--caption", help="Legenda do post, incluindo hashtags.")
    parser.add_argument("--caption-file", help="Arquivo de texto com a legenda (alternativa a --caption).")
    parser.add_argument("--dry-run", action="store_true", help="Valida tudo sem publicar de verdade.")
    args = parser.parse_args()
    if bool(args.caption) == bool(args.caption_file):
        parser.error("informe exatamente um entre --caption e --caption-file")
    caption = args.caption or Path(args.caption_file).read_text(encoding="utf-8").strip()
    run(args.images or args.image_urls, caption, args.dry_run, is_url=bool(args.image_urls))
