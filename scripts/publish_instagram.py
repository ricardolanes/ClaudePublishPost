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


def resolve_image_url(image: str) -> str:
    """Aceita uma URL publica pronta ou um caminho local (que sera hospedado)."""
    if image.startswith("http://") or image.startswith("https://"):
        print(f"  URL publica: {image}")
        return image
    return host_image(image)


def create_media_container(image_path: str, caption: str, is_carousel_item: bool) -> str:
    data = {"access_token": PAGE_TOKEN, "image_url": resolve_image_url(image_path)}
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


def run(images: list, caption: str, dry_run: bool = False):
    if not IG_ID or not PAGE_TOKEN:
        print("ERRO: credenciais nao encontradas. Preencha o arquivo .env na raiz do projeto"
              " (veja .env.example) antes de publicar.")
        sys.exit(1)
    if len(images) > 10:
        print("ERRO: maximo 10 imagens por post.")
        sys.exit(1)

    is_carousel = len(images) > 1
    print(f"\nPublicando {len(images)} imagem(ns) no Instagram...")
    if dry_run:
        print("[DRY RUN] Credenciais e imagens OK. Remova --dry-run para publicar de verdade.")
        return

    if is_carousel:
        print("\nPasso 1/3 - Criando containers do carrossel...")
        ids = [create_media_container(img, caption, is_carousel_item=True) for img in images]

        print("\nPasso 2/3 - Montando carrossel...")
        creation_id = create_carousel(ids, caption)
    else:
        print("\nPasso 1/2 - Criando container do post...")
        creation_id = create_media_container(images[0], caption, is_carousel_item=False)

    print(f"\nPasso {'3/3' if is_carousel else '2/2'} - Publicando...")
    if not wait_ready(creation_id):
        print("ERRO: timeout no processamento da imagem.")
        sys.exit(1)

    post_id = publish(creation_id)
    print("\nPublicado com sucesso!")
    print(f"Post ID: {post_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publica um post ou carrossel no Instagram via Meta Graph API.")
    parser.add_argument("--images", nargs="+", required=True,
                        help="De 1 a 10 imagens: caminho local (sera hospedado via catbox.moe)"
                             " ou URL publica ja acessivel (http/https), que a Graph API baixa direto."
                             " Em ambientes de nuvem, prefira a URL publica —"
                             " ex.: raw.githubusercontent.com apontando para um commit deste repo.")
    parser.add_argument("--caption", required=True, help="Legenda do post, incluindo hashtags.")
    parser.add_argument("--dry-run", action="store_true", help="Valida tudo sem publicar de verdade.")
    args = parser.parse_args()
    run(args.images, args.caption, args.dry_run)
