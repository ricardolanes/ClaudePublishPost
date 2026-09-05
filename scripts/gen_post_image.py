"""Gera a arte 1080x1080 do post: peças finalizadas em impressão 3D."""
import math
from pathlib import Path

W = H = 1080
FLOOR = 868

FONT = "Liberation Sans, DejaVu Sans, Helvetica, Arial, sans-serif"


def polar(cx, cy, r, a):
    return cx + r * math.cos(a), cy + r * math.sin(a)


def gear_path(cx, cy, r_out, r_in, teeth=12, phase=0.0):
    pts = []
    step = 2 * math.pi / teeth
    for i in range(teeth):
        a0 = phase + i * step
        for frac, r in ((0.00, r_in), (0.14, r_out), (0.36, r_out),
                        (0.50, r_in), (0.68, r_in), (0.85, r_in)):
            pts.append(polar(cx, cy, r, a0 + frac * step))
    d = "M {:.1f} {:.1f} ".format(*pts[0])
    d += " ".join("L {:.1f} {:.1f}".format(x, y) for x, y in pts[1:])
    return d + " Z"


def leaf(x, y, angle, length, width):
    """Folha simples: duas curvas espelhadas a partir da base."""
    a = math.radians(angle)
    tx, ty = x + length * math.sin(a), y - length * math.cos(a)
    # vetor perpendicular
    px, py = math.cos(a), math.sin(a)
    c1x, c1y = x + px * width + (tx - x) * 0.35, y + py * width + (ty - y) * 0.35
    c2x, c2y = x - px * width + (tx - x) * 0.35, y - py * width + (ty - y) * 0.35
    return (f"M {x:.1f} {y:.1f} Q {c1x:.1f} {c1y:.1f} {tx:.1f} {ty:.1f} "
            f"Q {c2x:.1f} {c2y:.1f} {x:.1f} {y:.1f} Z")


parts = []
add = parts.append

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}">')

# ---------------------------------------------------------------- defs
add('''<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#101220"/>
    <stop offset="0.55" stop-color="#171428"/>
    <stop offset="1" stop-color="#0d1018"/>
  </linearGradient>
  <radialGradient id="warm" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#ff7a1a" stop-opacity="0.30"/>
    <stop offset="1" stop-color="#ff7a1a" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="cool" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#4f8dff" stop-opacity="0.20"/>
    <stop offset="1" stop-color="#4f8dff" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="shadow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#04050a" stop-opacity="0.85"/>
    <stop offset="1" stop-color="#04050a" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="floorline" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.22"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
  </linearGradient>

  <linearGradient id="orange" x1="0" y1="0" x2="1" y2="0.2">
    <stop offset="0" stop-color="#ffb267"/>
    <stop offset="0.45" stop-color="#ff8a2b"/>
    <stop offset="1" stop-color="#d95a12"/>
  </linearGradient>
  <linearGradient id="orangeDark" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#e2701c"/>
    <stop offset="1" stop-color="#b4460c"/>
  </linearGradient>
  <linearGradient id="teal" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#7fdcff"/>
    <stop offset="0.5" stop-color="#38b6f0"/>
    <stop offset="1" stop-color="#1d78bd"/>
  </linearGradient>
  <linearGradient id="lav" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#cfccf5"/>
    <stop offset="0.5" stop-color="#a9a4e6"/>
    <stop offset="1" stop-color="#7a74c2"/>
  </linearGradient>
  <linearGradient id="green" x1="0" y1="1" x2="0.4" y2="0">
    <stop offset="0" stop-color="#2f8f5b"/>
    <stop offset="1" stop-color="#5fd39a"/>
  </linearGradient>

  <pattern id="dots" width="34" height="34" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.4" fill="#ffffff" fill-opacity="0.055"/>
  </pattern>
  <pattern id="layers" width="10" height="7" patternUnits="userSpaceOnUse">
    <rect x="0" y="0" width="10" height="7" fill="none"/>
    <rect x="0" y="5.6" width="10" height="1.4" fill="#000000" fill-opacity="0.16"/>
    <rect x="0" y="0" width="10" height="1.1" fill="#ffffff" fill-opacity="0.10"/>
  </pattern>
</defs>''')

# ---------------------------------------------------------------- fundo
add(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#dots)"/>')
add('<ellipse cx="215" cy="150" rx="560" ry="470" fill="url(#warm)"/>')
add('<ellipse cx="900" cy="960" rx="520" ry="420" fill="url(#cool)"/>')
add(f'<rect x="90" y="{FLOOR}" width="900" height="2" fill="url(#floorline)"/>')

# --------------------------------------------------------------- sombras
for cx, rx in ((330, 190), (585, 120), (795, 150)):
    add(f'<ellipse cx="{cx}" cy="{FLOOR + 14}" rx="{rx}" ry="26" fill="url(#shadow)"/>')

# ---------------------------------------------------------- engrenagem
GX, GY, GR = 800, FLOOR - 104, 104
add(f'<g transform="rotate(9 {GX} {GY})">')
add(f'<path d="{gear_path(GX, GY, GR, GR - 26, 12)}" fill="url(#teal)"/>')
add(f'<clipPath id="clipGear"><path d="{gear_path(GX, GY, GR, GR - 26, 12)}"/></clipPath>')
add(f'<rect x="{GX-GR}" y="{GY-GR}" width="{2*GR}" height="{2*GR}" '
    'fill="url(#layers)" clip-path="url(#clipGear)"/>')
add(f'<circle cx="{GX}" cy="{GY}" r="46" fill="#0f1320" fill-opacity="0.55"/>')
add(f'<circle cx="{GX}" cy="{GY}" r="30" fill="#101426"/>')
add(f'<circle cx="{GX}" cy="{GY}" r="30" fill="none" stroke="#8fe0ff" '
    'stroke-opacity="0.45" stroke-width="3"/>')
add(f'<path d="{gear_path(GX, GY, GR, GR - 26, 12)}" fill="none" '
    'stroke="#bdefff" stroke-opacity="0.28" stroke-width="2.5"/>')
add('</g>')

# ------------------------------------------------------- suporte de celular
SX = 585
stand = (f"M {SX-84} {FLOOR} L {SX+82} {FLOOR} L {SX+82} {FLOOR-26} "
         f"L {SX-16} {FLOOR-26} L {SX+34} {FLOOR-168} L {SX-4} {FLOOR-182} "
         f"L {SX-84} {FLOOR-34} Z")
add(f'<path d="{stand}" fill="url(#lav)"/>')
add(f'<clipPath id="clipStand"><path d="{stand}"/></clipPath>')
add(f'<rect x="{SX-90}" y="{FLOOR-190}" width="190" height="200" '
    'fill="url(#layers)" clip-path="url(#clipStand)"/>')
add(f'<path d="{stand}" fill="none" stroke="#e4e2ff" stroke-opacity="0.30" '
    'stroke-width="2.5" stroke-linejoin="round"/>')
# celular apoiado
add(f'<g transform="rotate(-16 {SX} {FLOOR-80})">')
add(f'<rect x="{SX-44}" y="{FLOOR-186}" width="92" height="156" rx="12" '
    'fill="#151a2b" stroke="#5b6488" stroke-width="2.5"/>')
add(f'<rect x="{SX-35}" y="{FLOOR-176}" width="74" height="130" rx="6" '
    'fill="#222a45" fill-opacity="0.9"/>')
add(f'<rect x="{SX-35}" y="{FLOOR-176}" width="74" height="130" rx="6" '
    'fill="url(#cool)"/>')
add('</g>')

# --------------------------------------------------------------- cachepô
PX = 330
p_top, p_bot = FLOOR - 196, FLOOR
top_w, bot_w = 116, 86
pot = (f"M {PX-top_w} {p_top} L {PX-bot_w} {p_bot-14} "
       f"Q {PX-bot_w} {p_bot} {PX-bot_w+16} {p_bot} "
       f"L {PX+bot_w-16} {p_bot} Q {PX+bot_w} {p_bot} {PX+bot_w} {p_bot-14} "
       f"L {PX+top_w} {p_top} Z")

# plantinha (atrás da borda do vaso)
add('<g>')
for ang, ln, wd in ((-46, 150, 30), (-22, 196, 34), (2, 224, 30),
                    (26, 190, 33), (48, 142, 28)):
    add(f'<path d="{leaf(PX, p_top + 6, ang, ln, wd)}" fill="url(#green)" '
        'stroke="#0f2a1e" stroke-opacity="0.35" stroke-width="2"/>')
add('</g>')

add(f'<ellipse cx="{PX}" cy="{p_top}" rx="{top_w}" ry="26" fill="#2b2440"/>')
add(f'<ellipse cx="{PX}" cy="{p_top+3}" rx="{top_w-16}" ry="19" fill="#181428"/>')
add(f'<path d="{pot}" fill="url(#orange)"/>')
add(f'<clipPath id="clipPot"><path d="{pot}"/></clipPath>')
add(f'<rect x="{PX-top_w-4}" y="{p_top}" width="{2*top_w+8}" height="220" '
    'fill="url(#layers)" clip-path="url(#clipPot)"/>')
# facetas hexagonais do cachepô
for off in (-58, 58):
    add(f'<path d="M {PX+off} {p_top} L {PX+off*0.74:.0f} {p_bot}" '
        'stroke="#000000" stroke-opacity="0.14" stroke-width="3" '
        'clip-path="url(#clipPot)"/>')
add(f'<path d="{pot}" fill="none" stroke="#ffcf9a" stroke-opacity="0.32" '
    'stroke-width="2.5"/>')
add(f'<ellipse cx="{PX}" cy="{p_top}" rx="{top_w}" ry="26" fill="none" '
    'stroke="#ffcf9a" stroke-opacity="0.30" stroke-width="2.5"/>')

# ------------------------------------------------------------ tipografia
add('<circle cx="76" cy="86" r="9" fill="#ff8a3d"/>')
add(f'<text x="102" y="94" font-family="{FONT}" font-size="26" font-weight="bold" '
    'letter-spacing="7" fill="#f4f1ff">IMPRESSÃO 3D</text>')

add(f'<text x="70" y="228" font-family="{FONT}" font-size="76" font-weight="bold" '
    'letter-spacing="-1.5" fill="#f7f5ff">Do arquivo</text>')
add(f'<text x="70" y="310" font-family="{FONT}" font-size="76" font-weight="bold" '
    'letter-spacing="-1.5" fill="#ff8a3d">à peça pronta.</text>')
add(f'<text x="72" y="368" font-family="{FONT}" font-size="24" letter-spacing="4.5" '
    'fill="#ffffff" fill-opacity="0.55">MODELAGEM  ·  IMPRESSÃO  ·  ACABAMENTO</text>')

add(f'<text x="1008" y="1000" text-anchor="end" font-family="{FONT}" font-size="30" '
    'letter-spacing="4" fill="#ffffff" fill-opacity="0.78">@bicoquente</text>')

add('</svg>')

svg = "\n".join(parts)

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="post",
                    help="Prefixo dos arquivos gerados (.svg e .html).")
    args = ap.parse_args()

    out = Path(args.out).with_suffix(".svg")
    out.write_text(svg, encoding="utf-8")
    html = out.with_suffix(".html")
    html.write_text(
        "<style>html,body{margin:0;padding:0;background:#101220;overflow:hidden;}"
        "svg{display:block;width:1080px;height:1080px;}</style>" + svg,
        encoding="utf-8")
    print(f"Gerado: {out} e {html}")
    print("Para rasterizar em PNG 1080x1080 (Chromium headless):")
    print(f"  chrome --headless --no-sandbox --hide-scrollbars "
          f"--window-size=1080,1200 --screenshot=raw.png {html}")
    print("  e recorte os 1080 px superiores (o viewport da janela inclui "
          "uma folga vertical).")
