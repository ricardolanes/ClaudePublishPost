"""Banco de cenas para sortear o assunto do post (impressora, peça pronta, filamento etc.).

Evita o viés do modelo (que sempre cai em vermelho/amarelo/azul/verde quando
pedimos "cores aleatórias" no prompt): o sorteio de cor acontece aqui, em
Python, a partir de uma paleta curada — não é o modelo quem escolhe.
"""
import random

STYLE = (
    "Professional product photography, cinematic color grading, warm tungsten "
    "key light with soft rim light, shallow depth of field, crisp detail, "
    "square 1:1 composition."
)

PALETTE = [
    "cobalt blue", "crimson red", "deep violet", "hot magenta", "emerald green",
    "sunset orange", "pearl white", "graphite black", "brushed gold", "teal",
    "lavender", "coral pink", "mustard yellow", "chrome silver",
]


def _spools() -> str:
    labels = ["PLA", "ABS", "PETG", "TPU"]
    colors = random.sample(PALETTE, len(labels))
    items = ", ".join(f'a {c} spool labeled "{l}"' for c, l in zip(colors, labels))
    return (
        f"Medium shot: four glossy 3D-printer filament spools standing side by side "
        f"on a dark reflective studio surface, motion-blurred colorful bokeh in the "
        f"background. From left to right: {items}, all spools fully inside the frame "
        f"with margin on every side. A single strand of filament unspools from the "
        f"rightmost reel and curves forward toward an illuminated 3D-printer nozzle "
        f"in the lower-right foreground, its tip glowing amber-hot, not covering any "
        f"label. {STYLE}"
    )


def _printer_mid_print() -> str:
    color = random.choice(PALETTE)
    return (
        f"Close-up of a 3D printer mid-print inside a dimly lit workshop: the hotend "
        f"glides across a partially finished object made of glossy {color} filament, "
        f"crisp horizontal layer lines visible, a faint wisp of heat haze near the "
        f"nozzle. Warm LED strip lighting along the printer frame, dark blurred "
        f"workshop background with soft bokeh. {STYLE}"
    )


def _finished_part() -> str:
    color = random.choice(PALETTE)
    obj = random.choice([
        "a mechanical gear", "a miniature dragon figurine", "a geometric vase",
        "a phone stand", "a articulated toy", "a honeycomb-pattern desk organizer",
    ])
    return (
        f"Studio product shot of {obj}, freshly 3D-printed in glossy {color} "
        f"plastic, resting on a dark wooden surface, visible clean layer lines "
        f"giving it a subtle ribbed texture, soft diffused light from the upper "
        f"left, a blurred workshop with tools in the background. {STYLE}"
    )


def _nozzle_macro() -> str:
    color = random.choice(PALETTE)
    return (
        f"Extreme macro shot of a 3D-printer nozzle extruding molten {color} "
        f"filament, the fresh layer glistening, tiny heat shimmer around the "
        f"brass nozzle tip, shallow focus with the rest of the print falling into "
        f"soft blur. Dramatic amber rim light. {STYLE}"
    )


def _flatlay() -> str:
    return (
        "Overhead flat-lay of assorted freshly 3D-printed objects (small gears, "
        "a miniature figurine, a phone stand, a geometric vase) arranged next to "
        "a spool of filament and a small tool, on a dark slate surface, soft "
        "top-down studio light with gentle shadows. " + STYLE
    )


def _hand_holding_part() -> str:
    color = random.choice(PALETTE)
    return (
        f"A person's hand holding a freshly 3D-printed {color} mechanical part "
        f"up to the light, inspecting the clean layer lines, blurred workshop "
        f"with a 3D printer glowing softly in the background. {STYLE}"
    )


SCENES = [
    ("carreteis_de_filamento", _spools),
    ("impressora_em_acao", _printer_mid_print),
    ("peca_pronta", _finished_part),
    ("macro_do_bico", _nozzle_macro),
    ("flat_lay_de_pecas", _flatlay),
    ("mao_segurando_peca", _hand_holding_part),
]


def pick_random_prompt() -> tuple[str, str]:
    """Sorteia uma cena e devolve (nome_da_cena, prompt)."""
    name, builder = random.choice(SCENES)
    return name, builder()
