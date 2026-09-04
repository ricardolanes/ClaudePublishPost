"""Publicação automática no Instagram via Meta Graph API."""
import argparse
import os
import re
import subprocess
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


def _raw_github_url(image_path: str) -> str | None:
    """Monta a URL raw.githubusercontent.com da imagem, se ela estiver commitada e a branch
    atual publicada no GitHub. Retorna None quando a imagem não está sob controle de versão
    ou o remoto não é o GitHub."""
    repo_root = Path(__file__).resolve().parent.parent
    try:
        remote = subprocess.run(
            ["git", "-C", str(repo_root), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        branch = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        tracked = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "--error-unmatch", str(Path(image_path).resolve())],
            capture_output=True, text=True, timeout=10,
        ).returncode == 0
    except (subprocess.SubprocessError, OSError):
        return None
    if not tracked or not branch:
        return None
    match = re.search(r"github\.com[:/]([^/]+)/([^/.]+?)(?:\.git)?$", remote)
    if not match:
        return None
    owner, repo = match.groups()
    rel_path = Path(image_path).resolve().relative_to(repo_root).as_posix()
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{rel_path}"


def host_image(image_path: str) -> str:
    """Hospeda a imagem em uma URL pública (a Graph API exige uma URL, não um arquivo local).

    Tenta catbox.moe primeiro; se o upload falhar (comum em IPs de datacenter/proxy de
    ambientes de nuvem), cai para a URL raw.githubusercontent.com da imagem, desde que ela
    já esteja commitada e a branch publicada no GitHub.
    """
    with open(image_path, "rb") as f:
        resp = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": (Path(image_path).name, f, "image/png")},
            timeout=60,
        )
    url = resp.text.strip()
    if url.startswith("https://"):
        print(f"  Hospedada (catbox.moe): {url}")
        return url

    fallback_url = _raw_github_url(image_path)
    if fallback_url is not None:
        check = requests.head(fallback_url, timeout=15)
        if check.status_code == 200:
            print(f"  catbox.moe falhou ({url}); usando raw.githubusercontent.com: {fallback_url}")
            return fallback_url

    raise RuntimeError(
        f"Falha no upload da imagem via catbox.moe: {url}\n"
        "  catbox.moe costuma bloquear IPs de datacenter/proxy (comum em"
        " ambientes de nuvem). Alternativa: faça commit da imagem e dê push da"
        " branch atual no repositorio, para que a URL raw.githubusercontent.com"
        " fique acessível como fallback automático."
    )


def create_media_container(image_path: str, caption: str, is_carousel_item: bool) -> str:
    data = {"access_token": PAGE_TOKEN, "image_url": host_image(image_path)}
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
    parser.add_argument("--images", nargs="+", required=True, help="Caminho de 1 a 10 imagens (PNG/JPG).")
    parser.add_argument("--caption", required=True, help="Legenda do post, incluindo hashtags.")
    parser.add_argument("--dry-run", action="store_true", help="Valida tudo sem publicar de verdade.")
    args = parser.parse_args()
    run(args.images, args.caption, args.dry_run)
