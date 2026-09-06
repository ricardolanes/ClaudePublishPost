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
        "a phone stand", "an articulated toy", "a honeycomb-pattern desk organizer",
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


def _pecas_na_mesa() -> str:
    return (
        "Eye-level shot of a wooden workshop desk cluttered with several freshly "
        "3D-printed parts of different colors (gears, brackets, a small figurine, "
        "a phone stand) scattered next to a filament spool, a scraper tool and a "
        "roll of blue tape, shallow depth of field with the nearest piece in "
        "sharp focus. " + STYLE
    )


def _impressora_bambu_a1() -> str:
    return (
        "A Bambu Lab A1 3D printer, open-frame CoreXY-style design with a black "
        "chassis and orange accents, sitting on a workshop desk, actively printing "
        "an object on its textured black-and-white speckled flexible build plate, "
        "the dual-gear direct-drive extruder visible on the print head, warm "
        "ambient light and a softly blurred workshop background. " + STYLE
    )


def _filamento_entrando_extrusora() -> str:
    color = random.choice(PALETTE)
    return (
        f"Extreme macro close-up of glossy {color} filament being fed into a "
        f"3D-printer extruder, the drive gears gripping the strand right at the "
        f"entry point, subtle motion blur on the gear teeth, warm rim light "
        f"catching the filament's surface. {STYLE}"
    )


def _camada_inicial() -> str:
    color = random.choice(PALETTE)
    return (
        f"Macro shot looking straight down at a 3D printer's first layer being "
        f"laid down in glossy {color} filament on a dark textured build plate, "
        f"the nozzle just past the corner leaving a crisp thin ribbon of plastic, "
        f"soft warm light grazing the plate's texture. {STYLE}"
    )


def _suportes_sendo_criados() -> str:
    color = random.choice(PALETTE)
    return (
        f"Close-up of a 3D print in progress in matte {color} filament, showing "
        f"a delicate lattice of support structures being built up beneath a "
        f"steep overhang, the nozzle actively laying down a thin support strand, "
        f"dramatic side lighting emphasizing the lattice geometry. {STYLE}"
    )


def _peca_em_meio_processo() -> str:
    color = random.choice(PALETTE)
    obj = random.choice([
        "a vase",
        "a plain unbranded full-face helmet shell (generic rounded shape, no"
        " visor cutout, no franchise markings)",
        "a generic humanoid robot figurine (original toy-like design, no"
        " franchise likeness)",
        "an architectural model",
    ])
    return (
        f"A 3D print of {obj} in glossy {color} filament, captured mid-process: "
        f"the bottom half fully printed with crisp layer lines, the top half "
        f"still missing, print head paused beside the unfinished top edge, dark "
        f"workshop background with soft bokeh. {STYLE}"
    )


def _acabamento_manual() -> str:
    color = random.choice(PALETTE)
    return (
        f"Close-up of hands manually finishing a freshly 3D-printed {color} "
        f"part on a workbench, one hand holding the piece steady while the "
        f"other uses a small file to smooth a support mark, fine plastic dust "
        f"visible in the warm side light, blurred workshop background. {STYLE}"
    )


def _pintura_da_peca() -> str:
    base_color = random.choice(PALETTE)
    paint_color = random.choice(PALETTE)
    return (
        f"Close-up of a hand carefully hand-painting a 3D-printed miniature "
        f"(originally {base_color} plastic) with a fine brush loaded with "
        f"{paint_color} acrylic paint, a small palette and brushes softly "
        f"blurred in the foreground, warm focused light on the model. {STYLE}"
    )


def _bobina_de_filamento() -> str:
    color = random.choice(PALETTE)
    return (
        f"Macro product shot of a single {color} 3D-printer filament spool "
        f"standing upright on a dark reflective surface, dramatic rim lighting "
        f"tracing the tightly wound strands, soft colorful bokeh in the "
        f"background, subtle reflection beneath the spool. {STYLE}"
    )


SCENES = [
    ("carreteis_de_filamento", _spools),
    ("impressora_em_acao", _printer_mid_print),
    ("peca_pronta", _finished_part),
    ("macro_do_bico", _nozzle_macro),
    ("flat_lay_de_pecas", _flatlay),
    ("mao_segurando_peca", _hand_holding_part),
    ("pecas_na_mesa", _pecas_na_mesa),
    ("impressora_bambu_a1", _impressora_bambu_a1),
    ("filamento_entrando_extrusora", _filamento_entrando_extrusora),
    ("camada_inicial", _camada_inicial),
    ("suportes_sendo_criados", _suportes_sendo_criados),
    ("peca_em_meio_processo", _peca_em_meio_processo),
    ("acabamento_manual", _acabamento_manual),
    ("pintura_da_peca", _pintura_da_peca),
    ("bobina_de_filamento", _bobina_de_filamento),
]


# Texto alternativo (acessibilidade) de cada cena, em pt-BR. Descreve o que
# aparece na imagem, sem citar cor: a cor e sorteada a cada geracao.
ALT_TEXTS = {
    "carreteis_de_filamento":
        "Quatro carreteis de filamento para impressao 3D lado a lado sobre uma superficie"
        " escura e reflexiva, com um fio saindo do ultimo carretel em direcao ao bico"
        " aquecido de uma impressora.",
    "impressora_em_acao":
        "Bico de uma impressora 3D deslizando sobre uma peca parcialmente impressa, com as"
        " linhas de camada visiveis, dentro de uma oficina com iluminacao quente.",
    "peca_pronta":
        "Peca recem-impressa em 3D sobre uma superficie de madeira escura, com as linhas de"
        " camada visiveis e uma oficina desfocada ao fundo.",
    "macro_do_bico":
        "Close extremo do bico de uma impressora 3D extrudando filamento derretido, com a"
        " camada recem-depositada ainda brilhando.",
    "flat_lay_de_pecas":
        "Vista de cima de varios objetos impressos em 3D — engrenagens, uma miniatura, um"
        " suporte de celular e um vaso — dispostos ao lado de um carretel de filamento.",
    "mao_segurando_peca":
        "Mao segurando uma peca recem-impressa em 3D contra a luz, examinando as linhas de"
        " camada, com uma impressora desfocada ao fundo.",
    "pecas_na_mesa":
        "Bancada de madeira com varias pecas impressas em 3D de cores diferentes espalhadas"
        " ao lado de um carretel de filamento e algumas ferramentas.",
    "impressora_bambu_a1":
        "Impressora 3D Bambu Lab A1, de estrutura aberta preta com detalhes laranja,"
        " imprimindo uma peca sobre a mesa texturizada.",
    "filamento_entrando_extrusora":
        "Close extremo do filamento sendo puxado para dentro da extrusora de uma impressora"
        " 3D, com as engrenagens tracionando o fio.",
    "camada_inicial":
        "Vista de cima da primeira camada de uma impressao 3D sendo depositada sobre a mesa"
        " texturizada, com o bico deixando uma fita fina de plastico.",
    "suportes_sendo_criados":
        "Impressao 3D em andamento mostrando a trelica de suportes sendo construida sob uma"
        " saliencia da peca.",
    "peca_em_meio_processo":
        "Peca impressa em 3D pela metade: a parte de baixo pronta com linhas de camada"
        " nitidas e o topo ainda faltando, com a cabeca de impressao parada ao lado.",
    "acabamento_manual":
        "Maos fazendo o acabamento manual de uma peca impressa em 3D numa bancada, usando"
        " uma lima pequena para alisar uma marca de suporte.",
    "pintura_da_peca":
        "Mao pintando uma miniatura impressa em 3D com um pincel fino, com paleta e pinceis"
        " desfocados em primeiro plano.",
    "bobina_de_filamento":
        "Close de um unico carretel de filamento para impressao 3D em pe sobre uma"
        " superficie escura e reflexiva, com luz de contorno destacando os fios enrolados.",
}


def alt_text_for(scene_name: str) -> str | None:
    """Texto alternativo da cena, usado como alt_text do post no Instagram."""
    return ALT_TEXTS.get(scene_name)


def pick_random_prompt(exclude: str | None = None) -> tuple[str, str]:
    """Sorteia uma cena (evitando repetir `exclude`, se houver mais de uma opção) e devolve (nome_da_cena, prompt)."""
    choices = [s for s in SCENES if s[0] != exclude] if exclude else SCENES
    name, builder = random.choice(choices or SCENES)
    return name, builder()
