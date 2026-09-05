"""Gera a imagem do post: quatro carretéis de filamento 3D em superfície reflexiva.

Constrói um SVG 1080x1080 e rasteriza com o Chromium headless.

Uso:
    python3 scripts/render_spools_image.py assets/posts/filament-spools.png
"""
import math
import subprocess
import sys
from pathlib import Path

W = H = 1080
CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    "/usr/bin/chromium",
    "/usr/bin/google-chrome",
]

# cx, cy, raio, rótulo, cor base, cor clara, cor escura
SPOOLS = [
    (218, 548, 122, "PLA", "#1f5fe0", "#6ea8ff", "#0b2a72"),
    (455, 505, 140, "ABS", "#d81f3a", "#ff7a86", "#6d0d1c"),
    (703, 528, 130, "PETG", "#6b21c8", "#b57bff", "#330d69"),
    (912, 560, 108, "TPU", "#e81ea0", "#ff86d2", "#71084e"),
]

TABLE_Y = 672
NOZZLE = (600, 762, 1.24)  # x, y, escala do hotend em primeiro plano


def spool(cx, cy, r, label, base, light, dark, idx):
    """Um carretel visto de frente: flange translúcida sobre o filamento enrolado."""
    g = []
    depth = r * 0.13
    ri, ro = r * 0.44, r * 0.87

    # volume: flange traseira deslocada
    g.append(
        f'<circle cx="{cx + depth:.1f}" cy="{cy - depth * 0.35:.1f}" r="{r:.1f}" '
        f'fill="#0e1017" opacity="0.95"/>'
    )
    g.append(
        f'<circle cx="{cx + depth * 0.55:.1f}" cy="{cy - depth * 0.2:.1f}" r="{r * 0.93:.1f}" '
        f'fill="{dark}" opacity="0.55"/>'
    )

    # filamento enrolado (anel)
    g.append(
        f'<path d="M {cx - ro:.1f} {cy:.1f} a {ro:.1f} {ro:.1f} 0 1 0 {ro * 2:.1f} 0 '
        f'a {ro:.1f} {ro:.1f} 0 1 0 {-ro * 2:.1f} 0 Z '
        f'M {cx - ri:.1f} {cy:.1f} a {ri:.1f} {ri:.1f} 0 1 1 {ri * 2:.1f} 0 '
        f'a {ri:.1f} {ri:.1f} 0 1 1 {-ri * 2:.1f} 0 Z" '
        f'fill="url(#wind{idx})" fill-rule="evenodd"/>'
    )

    # textura das voltas do filamento
    g.append(f'<g clip-path="url(#ring{idx})">')
    step = max(3.6, r * 0.031)
    n = int((ro - ri) / step)
    for k in range(n + 1):
        rr = ri + k * step
        op = 0.30 if k % 2 == 0 else 0.13
        col = "#000000" if k % 2 == 0 else "#ffffff"
        g.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" fill="none" '
            f'stroke="{col}" stroke-opacity="{op}" stroke-width="1.5"/>'
        )
    # brilho especular do enrolamento (luz quente do alto à esquerda)
    g.append(
        f'<ellipse cx="{cx - r * 0.42:.1f}" cy="{cy - r * 0.46:.1f}" '
        f'rx="{r * 0.52:.1f}" ry="{r * 0.38:.1f}" fill="url(#sheen)" '
        f'transform="rotate(-34 {cx - r * 0.42:.1f} {cy - r * 0.46:.1f})"/>'
    )
    g.append("</g>")

    # flange translúcida
    g.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="url(#flange)" opacity="0.72"/>'
    )
    g.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" '
        f'stroke="#0a0c12" stroke-width="{r * 0.07:.1f}"/>'
    )
    g.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.985:.1f}" fill="none" '
        f'stroke="{light}" stroke-opacity="0.30" stroke-width="1.6"/>'
    )
    # realce especular no topo-esquerda da flange
    g.append(
        f'<path d="M {cx - r * 0.90:.1f} {cy - r * 0.36:.1f} '
        f'A {r:.1f} {r:.1f} 0 0 1 {cx - r * 0.30:.1f} {cy - r * 0.92:.1f}" '
        f'fill="none" stroke="#ffe6bd" stroke-opacity="0.55" stroke-width="{r * 0.045:.1f}" '
        f'stroke-linecap="round" filter="url(#soft)"/>'
    )

    # cubo central
    g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{ri * 0.98:.1f}" fill="url(#hub)"/>')
    g.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{ri * 0.40:.1f}" fill="#05060a" '
        f'stroke="#3b4152" stroke-width="2"/>'
    )
    for a in range(0, 360, 60):
        hx = cx + ri * 0.68 * math.cos(math.radians(a))
        hy = cy + ri * 0.68 * math.sin(math.radians(a))
        g.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{ri * 0.13:.1f}" fill="#0a0c12" opacity="0.85"/>')

    # etiqueta
    lw, lh = r * 0.62, r * 0.235
    lx, ly = cx - lw / 2, cy + ri * 0.30
    g.append(
        f'<rect x="{lx:.1f}" y="{ly:.1f}" width="{lw:.1f}" height="{lh:.1f}" rx="{lh / 2:.1f}" '
        f'fill="#080a10" fill-opacity="0.92" stroke="{light}" stroke-opacity="0.55" stroke-width="1.4"/>'
    )
    g.append(
        f'<text x="{cx:.1f}" y="{ly + lh * 0.72:.1f}" text-anchor="middle" '
        f'font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="{lh * 0.62:.1f}" '
        f'font-weight="bold" letter-spacing="{lh * 0.09:.1f}" fill="{light}">{label}</text>'
    )
    return "\n".join(g)


def build_svg():
    p = []
    a = p.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    a("<defs>")
    a(
        '<linearGradient id="bg" x1="0" y1="0" x2="0.35" y2="1">'
        '<stop offset="0" stop-color="#0f0b17"/><stop offset="0.45" stop-color="#08090f"/>'
        '<stop offset="1" stop-color="#05060b"/></linearGradient>'
    )
    a(
        '<linearGradient id="table" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#0b0d17"/><stop offset="0.5" stop-color="#05060c"/>'
        '<stop offset="1" stop-color="#08040c"/></linearGradient>'
    )
    a(
        '<radialGradient id="key" cx="0.18" cy="0.10" r="0.75">'
        '<stop offset="0" stop-color="#ffb35c" stop-opacity="0.22"/>'
        '<stop offset="0.55" stop-color="#ff8a3d" stop-opacity="0.05"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0"/></radialGradient>'
    )
    a(
        '<radialGradient id="bounce" cx="0.5" cy="1" r="0.72">'
        '<stop offset="0" stop-color="#ff2fb0" stop-opacity="0.16"/>'
        '<stop offset="0.6" stop-color="#a01f8a" stop-opacity="0.05"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0"/></radialGradient>'
    )
    a(
        '<radialGradient id="bloom" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#ffd28a" stop-opacity="0.95"/>'
        '<stop offset="0.28" stop-color="#ff9d2e" stop-opacity="0.55"/>'
        '<stop offset="0.62" stop-color="#ff6a12" stop-opacity="0.20"/>'
        '<stop offset="1" stop-color="#ff5500" stop-opacity="0"/></radialGradient>'
    )
    a(
        '<radialGradient id="vig" cx="0.5" cy="0.48" r="0.76">'
        '<stop offset="0.4" stop-color="#000000" stop-opacity="0"/>'
        '<stop offset="0.72" stop-color="#000000" stop-opacity="0.42"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0.90"/></radialGradient>'
    )
    a(
        '<radialGradient id="sheen" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.42"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>'
    )
    a(
        '<radialGradient id="flange" cx="0.32" cy="0.26" r="0.85">'
        '<stop offset="0" stop-color="#8ea0c4" stop-opacity="0.30"/>'
        '<stop offset="0.45" stop-color="#39405a" stop-opacity="0.16"/>'
        '<stop offset="1" stop-color="#05060b" stop-opacity="0.55"/></radialGradient>'
    )
    a(
        '<radialGradient id="hub" cx="0.34" cy="0.28" r="0.8">'
        '<stop offset="0" stop-color="#333a4b"/><stop offset="0.6" stop-color="#171a24"/>'
        '<stop offset="1" stop-color="#0a0b11"/></radialGradient>'
    )
    a(
        '<linearGradient id="brass" x1="0" y1="0" x2="1" y2="0.3">'
        '<stop offset="0" stop-color="#6b4d13"/><stop offset="0.35" stop-color="#d8ae3f"/>'
        '<stop offset="0.62" stop-color="#f3d888"/><stop offset="1" stop-color="#7a5a17"/></linearGradient>'
    )
    a(
        '<linearGradient id="steel" x1="0" y1="0" x2="1" y2="0.2">'
        '<stop offset="0" stop-color="#2b3040"/><stop offset="0.4" stop-color="#6d7791"/>'
        '<stop offset="0.7" stop-color="#39405280"/><stop offset="1" stop-color="#1b1f2b"/></linearGradient>'
    )
    a(
        '<linearGradient id="strand" x1="0" y1="0" x2="1" y2="0.4">'
        '<stop offset="0" stop-color="#4f8dff"/><stop offset="0.34" stop-color="#ff4d63"/>'
        '<stop offset="0.62" stop-color="#c07bff"/><stop offset="0.82" stop-color="#ff45bb"/>'
        '<stop offset="1" stop-color="#ffb03a"/></linearGradient>'
    )
    a(
        '<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.34"/>'
        '<stop offset="0.55" stop-color="#ffffff" stop-opacity="0.06"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>'
    )
    a('<mask id="reflmask"><rect x="0" y="{}" width="{}" height="{}" fill="url(#fade)"/></mask>'.format(
        TABLE_Y - 40, W, H - TABLE_Y + 40))
    a('<filter id="soft"><feGaussianBlur stdDeviation="3"/></filter>')
    a('<filter id="glow"><feGaussianBlur stdDeviation="9"/></filter>')
    a('<filter id="farblur"><feGaussianBlur stdDeviation="26"/></filter>')
    a('<filter id="reflblur"><feGaussianBlur stdDeviation="7"/></filter>')
    a(
        '<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" '
        'numOctaves="2" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>'
    )
    for i, (cx, cy, r, _lb, base, light, dark) in enumerate(SPOOLS):
        ri, ro = r * 0.44, r * 0.87
        a(
            f'<radialGradient id="wind{i}" cx="0.34" cy="0.28" r="0.9">'
            f'<stop offset="0" stop-color="{light}"/><stop offset="0.45" stop-color="{base}"/>'
            f'<stop offset="1" stop-color="{dark}"/></radialGradient>'
        )
        a(
            f'<clipPath id="ring{i}"><path d="M {cx - ro:.1f} {cy:.1f} '
            f'a {ro:.1f} {ro:.1f} 0 1 0 {ro * 2:.1f} 0 a {ro:.1f} {ro:.1f} 0 1 0 {-ro * 2:.1f} 0 Z '
            f'M {cx - ri:.1f} {cy:.1f} a {ri:.1f} {ri:.1f} 0 1 1 {ri * 2:.1f} 0 '
            f'a {ri:.1f} {ri:.1f} 0 1 1 {-ri * 2:.1f} 0 Z" clip-rule="evenodd"/></clipPath>'
        )
    a("</defs>")

    # --- fundo -------------------------------------------------------------
    a(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    a('<g filter="url(#farblur)" opacity="0.85">')
    ribbons = [
        ("M -120 250 C 180 90, 520 330, 900 140 S 1180 330, 1240 260", "#1d4fd8", 150, 0.22),
        ("M -120 400 C 220 250, 470 470, 860 300 S 1160 430, 1240 380", "#7a1fd0", 120, 0.19),
        ("M -120 130 C 240 30, 600 190, 980 40 S 1200 150, 1240 120", "#e01f8a", 90, 0.15),
        ("M -120 560 C 260 430, 640 620, 1000 470 S 1200 560, 1240 540", "#ff7a1f", 70, 0.10),
    ]
    for d, col, wdt, op in ribbons:
        a(f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity="{op}" stroke-width="{wdt}" stroke-linecap="round"/>')
    # formas translúcidas em camadas
    a('<ellipse cx="330" cy="300" rx="270" ry="210" fill="#3b1f8f" fill-opacity="0.10" transform="rotate(-16 330 300)"/>')
    a('<ellipse cx="820" cy="230" rx="240" ry="180" fill="#0f3ea8" fill-opacity="0.10" transform="rotate(12 820 230)"/>')
    a('<circle cx="900" cy="360" r="180" fill="#c01f7a" fill-opacity="0.09"/>')
    a('<circle cx="250" cy="470" r="150" fill="#ff8a1f" fill-opacity="0.06"/>')
    a("</g>")
    a(f'<rect width="{W}" height="{H}" fill="url(#key)"/>')

    # --- superfície reflexiva ----------------------------------------------
    a(f'<rect x="0" y="{TABLE_Y}" width="{W}" height="{H - TABLE_Y}" fill="url(#table)"/>')
    a(f'<rect x="0" y="{TABLE_Y - 2}" width="{W}" height="3" fill="#5b6480" opacity="0.35"/>')

    # reflexos dos carretéis
    a('<g mask="url(#reflmask)" filter="url(#reflblur)" opacity="0.55">')
    for i, (cx, cy, r, lb, base, light, dark) in enumerate(SPOOLS):
        baseline = cy + r
        a(f'<g transform="translate(0 {2 * baseline:.1f}) scale(1 -1)">')
        a(spool(cx, cy, r, lb, base, light, dark, i))
        a("</g>")
    a("</g>")

    # sombras de contato
    for cx, cy, r, *_ in SPOOLS:
        a(
            f'<ellipse cx="{cx:.1f}" cy="{cy + r - 4:.1f}" rx="{r * 0.95:.1f}" ry="{r * 0.14:.1f}" '
            f'fill="#000000" opacity="0.60" filter="url(#glow)"/>'
        )

    # --- carretéis ----------------------------------------------------------
    for i, (cx, cy, r, lb, base, light, dark) in enumerate(SPOOLS):
        a(spool(cx, cy, r, lb, base, light, dark, i))

    # --- fio de filamento arqueando até o bico ------------------------------
    strand = (
        "M 268 448 C 336 356, 404 360, 456 392 C 512 428, 566 356, 640 384 "
        "C 716 412, 764 372, 862 440 C 918 480, 902 556, 832 602 "
        "C 762 648, 664 566, 606 590"
    )
    a(f'<path d="{strand}" fill="none" stroke="url(#strand)" stroke-opacity="0.35" stroke-width="16" stroke-linecap="round" filter="url(#glow)"/>')
    a(f'<path d="{strand}" fill="none" stroke="url(#strand)" stroke-width="6" stroke-linecap="round"/>')
    a(f'<path d="{strand}" fill="none" stroke="#ffffff" stroke-opacity="0.35" stroke-width="1.6" stroke-linecap="round" transform="translate(-1.4 -1.4)"/>')

    # --- bico quente em primeiro plano --------------------------------------
    nx, ny, ns = NOZZLE
    a(f'<g transform="translate({nx} {ny}) scale({ns})">{nozzle()}</g>')

    # --- luz de rebote magenta + vinheta ------------------------------------
    a(f'<rect width="{W}" height="{H}" fill="url(#bounce)"/>')
    a(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')

    # --- assinatura ----------------------------------------------------------
    a(
        '<text x="1016" y="1030" text-anchor="end" font-family="DejaVu Sans, Liberation Sans, sans-serif" '
        'font-size="26" letter-spacing="3" fill="#ffffff" fill-opacity="0.80">@bicoquente</text>'
    )
    a(f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.045" style="mix-blend-mode:overlay"/>')
    a("</svg>")
    return "\n".join(p)


def nozzle():
    """Hotend em primeiro plano com bico incandescente, desenhado na origem."""
    g = []
    # halo de calor projetado na superfície
    g.append('<ellipse cx="0" cy="128" rx="265" ry="140" fill="url(#bloom)" opacity="0.85"/>')
    # dissipador
    for k in range(4):
        y = -150 + k * 27
        g.append(
            f'<rect x="-68" y="{y}" width="136" height="17" rx="7" fill="url(#steel)" '
            f'stroke="#0a0c12" stroke-width="1.5"/>'
        )
    # garganta
    g.append('<rect x="-22" y="-44" width="44" height="32" rx="6" fill="#232838" stroke="#0a0c12" stroke-width="1.5"/>')
    # bloco aquecedor
    g.append('<rect x="-80" y="-14" width="160" height="76" rx="10" fill="#20242f" stroke="#0a0c12" stroke-width="2"/>')
    g.append('<rect x="-80" y="-14" width="160" height="76" rx="10" fill="#ff6a12" fill-opacity="0.22"/>')
    g.append('<circle cx="-48" cy="26" r="13" fill="#0a0c12" stroke="#4a5265" stroke-width="2"/>')
    g.append('<circle cx="48" cy="26" r="10" fill="#ffb247" opacity="0.9" filter="url(#soft)"/>')
    g.append('<rect x="-80" y="-14" width="160" height="10" rx="5" fill="#ffffff" fill-opacity="0.10"/>')
    # bico cônico
    g.append(
        '<path d="M -40 62 L 40 62 L 15 118 L 8 134 L -8 134 L -15 118 Z" '
        'fill="url(#brass)" stroke="#120c04" stroke-width="2"/>'
    )
    g.append('<path d="M -33 68 L -11 118" stroke="#fff0c2" stroke-opacity="0.55" stroke-width="4" stroke-linecap="round"/>')
    # ponta incandescente
    g.append('<ellipse cx="0" cy="130" rx="95" ry="72" fill="url(#bloom)"/>')
    g.append('<rect x="-9" y="124" width="18" height="14" rx="4" fill="#ffe9b0"/>')
    g.append('<circle cx="0" cy="143" r="11" fill="#fff2cf" filter="url(#soft)"/>'
    )
    g.append(
        '<path d="M -80 60 L 80 60" stroke="#ffb04a" stroke-opacity="0.75" stroke-width="4" '
        'stroke-linecap="round" filter="url(#soft)"/>')
    # filete extrudado
    g.append(
        '<path d="M 0 147 C 3 168, -14 176, -32 184" fill="none" stroke="#ffab3d" '
        'stroke-width="7" stroke-linecap="round" opacity="0.9"/>'
    )
    g.append('<ellipse cx="-38" cy="187" rx="24" ry="8" fill="#ff9a2e" opacity="0.4" filter="url(#soft)"/>')
    return "\n".join(g)


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "assets/posts/filament-spools.png").resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    svg = build_svg()
    tmp = out.with_suffix(".svg")
    tmp.write_text(svg, encoding="utf-8")
    html = out.with_suffix(".html")
    html.write_text(
        f'<html><body style="margin:0;background:#07080e">{svg}</body></html>', encoding="utf-8"
    )

    chrome = next((c for c in CHROME_CANDIDATES if Path(c).exists()), None)
    if not chrome:
        raise SystemExit("Chromium nao encontrado para rasterizar o SVG.")
    # O viewport do headless fica ~85px mais baixo que --window-size, entao
    # renderizamos com folga (e em 2x) e recortamos os 1080x1080 do topo.
    scale, slack = 2, 160
    shot = out.with_name(out.stem + "-raw.png")
    subprocess.run(
        [chrome, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
         f"--force-device-scale-factor={scale}", f"--window-size={W},{H + slack}",
         f"--screenshot={shot}", f"file://{html}"],
        check=True, capture_output=True,
    )

    from PIL import Image

    img = Image.open(shot).convert("RGB")
    if img.height < H * scale or img.width < W * scale:
        raise SystemExit(f"Render incompleto: {img.size}, esperado >= {W * scale}x{H * scale}")
    img = img.crop((0, 0, W * scale, H * scale)).resize((W, H), Image.LANCZOS)
    img.save(out, "PNG")

    shot.unlink()
    html.unlink()
    tmp.unlink()
    print(f"Imagem gerada: {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
