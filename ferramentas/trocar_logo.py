#!/usr/bin/env python3
"""
Troca o logo provisorio pelo logo real da empresa.

Uso:
    python ferramentas/trocar_logo.py logo.png
    python ferramentas/trocar_logo.py logo.png --icone simbolo.png

  logo.png     Logo completo (pode ser horizontal, com o nome escrito).
               Aparece no topo do assistente de conexao.
  --icone      Opcional. Versao quadrada do logo (so o simbolo), usada como
               icone do programa, da bandeja e do menu Iniciar. Se nao for
               informado, o proprio logo e centralizado num quadrado.

Formatos aceitos: PNG (de preferencia com fundo transparente) ou JPG.
Tamanho recomendado: pelo menos 512 px no lado maior.

Requer: pip install pillow
"""
import argparse
import base64
import io
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Instale o Pillow antes: pip install pillow")

KIT = Path(__file__).resolve().parent.parent
PASTA = KIT / "marca" / "theme" / "colored"
NOME_CURTO = "ConteudosRadios"
COR_PRINCIPAL = "#00457C"


def carregar(caminho: Path) -> Image.Image:
    img = Image.open(caminho).convert("RGBA")
    # Recorta bordas totalmente transparentes
    caixa = img.getchannel("A").getbbox()
    return img.crop(caixa) if caixa else img


def luminosidade_media(img: Image.Image) -> float:
    pequeno = img.copy()
    pequeno.thumbnail((128, 128))
    total = soma = 0.0
    dados = pequeno.tobytes()
    for i in range(0, len(dados), 4):
        r, g, b, a = dados[i:i + 4]
        if a > 128:
            soma += (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
            total += 1
    return soma / total if total else 1.0


def encaixar(img: Image.Image, largura: int, altura: int, margem: float) -> Image.Image:
    tela = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    maxw, maxh = int(largura * (1 - 2 * margem)), int(altura * (1 - 2 * margem))
    # Escala para caber (aumenta ou diminui, mantendo a proporcao)
    escala = min(maxw / img.width, maxh / img.height)
    copia = img.resize((max(1, round(img.width * escala)), max(1, round(img.height * escala))), Image.LANCZOS)
    tela.alpha_composite(copia, ((largura - copia.width) // 2, (altura - copia.height) // 2))
    return tela


def caixa_branca(img: Image.Image, raio: int) -> Image.Image:
    fundo = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(fundo).rounded_rectangle((0, 0, img.width - 1, img.height - 1), raio, fill="white")
    fundo.alpha_composite(img)
    return fundo


def svg_com_png(img: Image.Image, comentario: str) -> str:
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    dados = base64.b64encode(buf.getvalue()).decode()
    w, h = img.size
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<!-- {comentario} -->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'  <image width="{w}" height="{h}" xlink:href="data:image/png;base64,{dados}"/>\n</svg>\n')


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("logo", type=Path)
    p.add_argument("--icone", type=Path, help="versao quadrada do logo")
    p.add_argument("--sem-caixa-branca", action="store_true",
                   help="nunca colocar fundo branco atras do logo do assistente")
    a = p.parse_args()

    logo = carregar(a.logo)
    icone = carregar(a.icone) if a.icone else logo

    # Icone do programa (256x256). Logo escuro ganha um quadrado branco
    # arredondado para aparecer bem na barra de tarefas escura do Windows.
    base_icone = encaixar(icone, 1024, 1024, 0.06)
    if luminosidade_media(icone) < 0.45:
        base_icone = caixa_branca(encaixar(icone, 1024, 1024, 0.12), 210)
    base_icone = base_icone.resize((512, 512), Image.LANCZOS)
    (PASTA / f"{NOME_CURTO}-icon.svg").write_text(
        svg_com_png(base_icone, "Icone do programa"), encoding="utf-8")

    # Bloco do menu Iniciar: o fundo ja e azul (definido no manifesto)
    tile = encaixar(icone, 512, 512, 0.14)
    (PASTA / f"{NOME_CURTO}-w10startmenu.svg").write_text(
        svg_com_png(tile, "Bloco do menu Iniciar"), encoding="utf-8")

    # Logo do assistente: area de ate 2:1 sobre o cabecalho azul
    assistente = encaixar(logo, 532, 252, 0.04)
    if luminosidade_media(logo) < 0.6 and not a.sem_caixa_branca:
        print("Logo escuro detectado: colocando fundo branco atras dele no assistente.")
        assistente = caixa_branca(encaixar(logo, 532, 252, 0.10), 28)
    (PASTA / "wizard_logo.svg").write_text(
        svg_com_png(assistente, "Logo do assistente de conexao"), encoding="utf-8")
    assistente.resize((266, 126), Image.LANCZOS).save(PASTA / "wizard_logo@2x.png")
    assistente.resize((133, 63), Image.LANCZOS).save(PASTA / "wizard_logo.png")

    print(f"Logo aplicado. Arquivos atualizados em {PASTA}")


if __name__ == "__main__":
    main()
