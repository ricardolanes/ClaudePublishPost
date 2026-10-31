"""Cenas disponíveis para geração das imagens dos posts de impressão 3D.

Cada cena tem:
  - key:    identificador curto e estável (usado no lock de não-repetição)
  - label:  nome legível em pt-BR (mostrado como "Cena sorteada")
  - prompt: descrição enviada ao modelo de imagem
"""

STYLE = (
    "Fotografia realista, qualidade editorial para Instagram, iluminação suave e "
    "difusa, profundidade de campo rasa, cores ricas mas naturais, foco nítido, "
    "composição quadrada 1:1, aparência de foto real tirada com câmera DSLR. "
    "Sem texto, sem letras, sem logotipos, sem marcas d'água."
)

SCENES = [
    {
        "key": "filament_spools",
        "label": "Carretéis de filamento",
        "prompt": (
            "Vários carretéis de filamento para impressora 3D organizados numa "
            "estante de madeira clara, cores variadas (laranja, azul petróleo, "
            "cinza, branco), filamento visivelmente enrolado em cada carretel."
        ),
    },
    {
        "key": "printer_in_action",
        "label": "Impressora em ação",
        "prompt": (
            "Impressora 3D FDM em pleno funcionamento, bico extrusor depositando "
            "filamento numa peça parcialmente construída, leve brilho do plástico "
            "quente, bancada de oficina ao fundo levemente desfocada."
        ),
    },
    {
        "key": "finished_part",
        "label": "Peça finalizada",
        "prompt": (
            "Peça impressa em 3D recém-finalizada sobre a mesa de impressão, "
            "camadas visíveis e regulares, geometria limpa e bem resolvida, "
            "acabamento fosco."
        ),
    },
    {
        "key": "nozzle_macro",
        "label": "Macro do bico extrusor",
        "prompt": (
            "Macro extrema do bico extrusor de uma impressora 3D, filamento "
            "derretido saindo em um filete fino e brilhante, detalhes metálicos "
            "do hotend, fundo escuro desfocado."
        ),
    },
    {
        "key": "flat_lay",
        "label": "Flat lay de impressão 3D",
        "prompt": (
            "Flat lay visto de cima: peças impressas em 3D, um carretel de "
            "filamento, alicate de corte, espátula e chave Allen, dispostos com "
            "capricho sobre fundo de concreto claro."
        ),
    },
    {
        "key": "hand_holding_part",
        "label": "Mão segurando uma peça",
        "prompt": (
            "Mão humana segurando delicadamente uma peça impressa em 3D contra a "
            "luz da janela, camadas de impressão bem visíveis, sensação tátil e "
            "artesanal, fundo desfocado."
        ),
    },
    {
        "key": "parts_on_table",
        "label": "Peças sobre a mesa",
        "prompt": (
            "Conjunto de várias peças impressas em 3D de tamanhos e cores "
            "diferentes espalhadas sobre uma mesa de madeira, luz lateral suave "
            "destacando as texturas das camadas."
        ),
    },
    {
        "key": "bambu_a1",
        "label": "Impressora Bambu Lab A1",
        "prompt": (
            "Impressora 3D moderna de pórtico aberto, estilo cartesiano compacto "
            "com haste vertical e trilho único, corpo cinza e preto, numa bancada "
            "arrumada de ateliê, imprimindo uma peça pequena."
        ),
    },
    {
        "key": "filament_feeding",
        "label": "Filamento entrando na extrusora",
        "prompt": (
            "Close do filamento sendo tracionado para dentro do conjunto "
            "extrusor de uma impressora 3D, tubo guia de PTFE, engrenagem de "
            "tração visível, foco preciso no ponto de entrada."
        ),
    },
    {
        "key": "first_layer",
        "label": "Primeira camada",
        "prompt": (
            "Close rasante da primeira camada de uma impressão 3D sendo "
            "depositada na mesa de impressão texturizada, linhas paralelas "
            "perfeitamente uniformes e bem aderidas, reflexo suave na superfície."
        ),
    },
    {
        "key": "supports_building",
        "label": "Suportes sendo construídos",
        "prompt": (
            "Impressão 3D em andamento mostrando estruturas de suporte "
            "ramificadas e finas sustentando as partes salientes da peça, "
            "treliça delicada de plástico, foco nítido nos suportes."
        ),
    },
    {
        "key": "part_mid_print",
        "label": "Peça no meio da impressão",
        "prompt": (
            "Peça impressa em 3D na metade do processo, parte inferior já "
            "concluída e topo aberto revelando o preenchimento interno em favo "
            "de mel, bico extrusor logo acima."
        ),
    },
    {
        "key": "manual_finishing",
        "label": "Acabamento manual",
        "prompt": (
            "Mãos fazendo o acabamento manual de uma peça impressa em 3D com "
            "lixa e estilete de precisão, pequenas aparas de plástico sobre a "
            "bancada, luz de trabalho focada."
        ),
    },
    {
        "key": "painting_a_part",
        "label": "Pintura de uma peça",
        "prompt": (
            "Peça impressa em 3D sendo pintada à mão com pincel fino, potes de "
            "tinta acrílica ao redor, cores sendo aplicadas sobre a base "
            "primerizada, bancada de hobby bem iluminada."
        ),
    },
    {
        "key": "single_spool_closeup",
        "label": "Close de um carretel",
        "prompt": (
            "Close de um único carretel de filamento para impressão 3D, "
            "filamento enrolado em espiral perfeita, cor vibrante, leve brilho "
            "no plástico, fundo neutro e desfocado."
        ),
    },
]

SCENES_BY_KEY = {s["key"]: s for s in SCENES}


def build_prompt(scene: dict) -> str:
    """Monta o prompt final enviado ao modelo de imagem."""
    return f"{scene['prompt']} {STYLE}"
