"""
Gera o portfólio de Douglas de Oliveira em estilo Suíço (International Typographic Style).

Formato: 16:9 (960 x 540 pt).
Grid: 12 colunas, margem 48 pt, calha 14 pt.
Tipografia: Helvetica / Helvetica-Bold (fonte padrão do PDF, sem dependências externas).
Paleta: papel, preto e um azul de destaque (cor da marca).

Uso (a partir da raiz do repositório):
    python3 portfolio/build_portfolio.py

Requer: reportlab, pillow.
Os assets ficam em portfolio/assets (gerados por prepare_assets.py a partir do PDF original).
"""

import os
import tempfile

from PIL import Image, ImageEnhance
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "Portfolio Douglas de Oliveira - Swiss 16x9.pdf")

# ---------------------------------------------------------------- dimensões
W, H = 960, 540
M = 48                  # margem
GUT = 14                # calha
COLS = 12
COL_W = (W - 2 * M - (COLS - 1) * GUT) / COLS


def X(col):
    """Coordenada x do início de uma coluna do grid (0 a 12)."""
    return M + col * (COL_W + GUT)


def SPAN(n):
    """Largura de n colunas."""
    return n * COL_W + (n - 1) * GUT


# ---------------------------------------------------------------- cores
PAPER = HexColor("#F3F2EE")
INK = HexColor("#0D0D0D")
BLUE = HexColor("#1648FF")
CYAN = HexColor("#7FE7FF")
GRAY = HexColor("#6E6E6E")
RULE = HexColor("#0D0D0D")
LIGHT_RULE = HexColor("#CFCBC2")
TRACK = HexColor("#DAD8D0")

REG = "Helvetica"
BOLD = "Helvetica-Bold"
TOTAL_PAGES = 10


# ---------------------------------------------------------------- helpers de texto
def ty(top):
    """Converte coordenada de topo (y para baixo) em coordenada PDF (y para cima)."""
    return H - top


def text(c, x, top, s, font=REG, size=12, color=INK, cs=0.0):
    """Texto com linha de base em `top`. cs = espaçamento entre letras (tracking)."""
    t = c.beginText(x, ty(top))
    t.setFont(font, size)
    t.setFillColor(color)
    t.setCharSpace(cs)  # sempre explícito: o estado de texto vaza entre blocos BT/ET
    t.textOut(s)
    c.drawText(t)


def text_right(c, xr, top, s, font=REG, size=12, color=INK):
    text(c, xr - stringWidth(s, font, size), top, s, font, size, color)


def fit_size(s, font, max_size, max_w):
    """Maior tamanho (até max_size) em que a string cabe em max_w."""
    w = stringWidth(s, font, 1)
    return min(max_size, max_w / w)


def paragraph(c, x, top, width, s, font=REG, size=12, leading=None, color=INK):
    """Parágrafo com quebra automática. Retorna o topo da próxima linha."""
    leading = leading or size * 1.4
    lines = simpleSplit(s, font, size, width)
    for ln in lines:
        text(c, x, top, ln, font, size, color)
        top += leading
    return top


def rule(c, x1, x2, top, color=RULE, width=0.6):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, ty(top), x2, ty(top))


def rect(c, x, top, w, h, color, alpha=None):
    c.setFillColor(color)
    if alpha is not None:
        c.setFillAlpha(alpha)
    c.rect(x, ty(top) - h, w, h, stroke=0, fill=1)
    if alpha is not None:
        c.setFillAlpha(1)


def header(c, section, n, color=INK, rule_color=None, rule_end=W - M):
    """Cabeçalho padrão: seção à esquerda, numeração à direita, filete abaixo."""
    rule_color = rule_color or color
    text(c, M, 30, section.upper(), BOLD, 8, color, cs=0.8)
    text_right(c, W - M, 30, f"{n:02d} / {TOTAL_PAGES:02d}", BOLD, 8, color)
    rule(c, M, rule_end, 42, rule_color, 0.7)


def footer_name(c, color=INK, top=512):
    text(c, M, top, "DOUGLAS ANTÔNIO GOMES DE OLIVEIRA", BOLD, 7, color, cs=0.6)


def asset(name):
    return os.path.join(ASSETS, name)


def cover_crop(path, w, h, anchor=(0.5, 0.0)):
    """Recorta a imagem para a proporção w:h (preenchendo a moldura).
    anchor = (horizontal, vertical) em 0..1; (0.5, 0) mantém o topo."""
    im = Image.open(path).convert("RGBA")
    iw, ih = im.size
    target = w / h
    if iw / ih > target:           # imagem mais larga: corta laterais
        nw = int(ih * target)
        left = int((iw - nw) * anchor[0])
        im = im.crop((left, 0, left + nw, ih))
    else:                          # imagem mais alta: corta em cima/baixo
        nh = int(iw / target)
        top = int((ih - nh) * anchor[1])
        im = im.crop((0, top, iw, top + nh))
    fd, tmp = tempfile.mkstemp(suffix=".png", dir=tempfile.gettempdir())
    os.close(fd)
    im.save(tmp)
    return tmp


def trim_alpha(path):
    """Remove margens transparentes de um PNG com alfa."""
    im = Image.open(path).convert("RGBA")
    bbox = im.getchannel("A").getbbox()
    if bbox:
        im = im.crop(bbox)
    fd, tmp = tempfile.mkstemp(suffix=".png", dir=tempfile.gettempdir())
    os.close(fd)
    im.save(tmp)
    return tmp


def draw_fit_center(c, path, cx, cy_top, max_w, max_h, mask="auto"):
    """Centraliza a imagem em (cx, cy_top) respeitando max_w x max_h."""
    im = Image.open(path)
    iw, ih = im.size
    s = min(max_w / iw, max_h / ih)
    dw, dh = iw * s, ih * s
    c.drawImage(path, cx - dw / 2, ty(cy_top) - dh / 2, width=dw, height=dh, mask=mask)


# ---------------------------------------------------------------- slides
def slide_cover(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # bloco azul à direita, com o retrato recortado sobre ele (bleed à direita e à base)
    bx = X(7) + COL_W / 2 + GUT / 2
    rect(c, bx, 0, W - bx, H, BLUE)
    portrait = trim_alpha(asset("cover_portrait.png"))
    ph = 440
    pw = ph * Image.open(portrait).size[0] / Image.open(portrait).size[1]
    c.drawImage(portrait, (bx + W) / 2 - pw / 2, 0, width=pw, height=ph, mask="auto")

    # topo (filete e numeração ficam fora da faixa azul)
    text(c, M, 30, "PORTFÓLIO 2026", BOLD, 8, INK, cs=0.8)
    rule(c, M, bx - GUT, 42, INK, 0.7)
    text_right(c, bx - GUT, 30, "01 / 10", BOLD, 8, INK)

    # nome em três linhas, abaixo do filete do cabeçalho
    name_w = X(7) - M - GUT
    lines = ["DOUGLAS", "DE", "OLIVEIRA"]
    size = min(fit_size(l, BOLD, 104, name_w) for l in lines)
    for i, ln in enumerate(lines):
        text(c, M - 4, 150 + i * size * 0.92, ln, BOLD, size, INK, cs=-size * 0.025)

    # subtítulo e cargo
    text(c, M, 396, "Designer Gráfico /", REG, 22, INK)
    text(c, M, 424, "Web designer", REG, 22, BLUE)

    # rodapé do grid
    rule(c, M, X(7) - GUT, 470, INK, 0.7)
    text(c, M, 486, "Belo Horizonte, MG", BOLD, 8, INK, cs=0.6)
    text(c, M + 160, 486, "PORTFÓLIO · CURRÍCULO VISUAL", BOLD, 8, INK, cs=0.6)
    c.showPage()


def slide_about(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    header(c, "Sobre", 2)

    # título
    text(c, M - 3, 92, "Formação", BOLD, 58, INK, cs=-1.2)
    text(c, M - 3, 150, "e habilidades", BOLD, 58, INK, cs=-1.2)

    # coluna esquerda: formação
    lx, lw = X(0), SPAN(6)
    text(c, lx, 262, "FORMAÇÃO", BOLD, 8, BLUE, cs=0.8)
    entries = [
        ("2026", "Publicidade e Propaganda", "Universidade Federal de Minas Gerais (UFMG)"),
        ("2022", "Designer Gráfico", "Escola Casa"),
        ("2018", "Editor de vídeo / Motion Graphic", "Ozi Escola de Audiovisual"),
    ]
    top = 282
    for year, title, inst in entries:
        rule(c, lx, lx + lw, top, INK, 0.7)
        text(c, lx, top + 38, year, BOLD, 30, BLUE, cs=-0.5)
        text(c, lx + 110, top + 30, title, BOLD, 16, INK)
        text(c, lx + 110, top + 50, inst, REG, 11, GRAY)
        top += 74
    rule(c, lx, lx + lw, top, INK, 0.7)

    # coluna direita: habilidades
    rx, rw = X(6), SPAN(6)
    text(c, rx, 262, "HABILIDADES", BOLD, 8, BLUE, cs=0.8)
    skills = [("Design gráfico", 90), ("Edição de vídeo", 80), ("Webdesign", 80)]
    top = 282
    for name, pct in skills:
        rule(c, rx, rx + rw, top, INK, 0.7)
        text(c, rx, top + 30, name, BOLD, 16, INK)
        text_right(c, rx + rw, top + 38, f"{pct}%", BOLD, 30, INK)
        bar_top = top + 52
        rect(c, rx, bar_top, rw, 8, TRACK)
        rect(c, rx, bar_top, rw * pct / 100, 8, BLUE)
        top += 74
    rule(c, rx, rx + rw, top, INK, 0.7)

    footer_name(c, GRAY, 526)
    c.showPage()


def slide_social_showcase(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    header(c, "Experiência · Social media", 3)

    text(c, M, 92, "Social", BOLD, 58, INK, cs=-1.2)
    text(c, M, 150, "media", BOLD, 58, INK, cs=-1.2)
    paragraph(c, M, 210, SPAN(3) + 20,
              "Peças de campanha para a RTT: promoções, datas comemorativas e "
              "divulgação de produtos para redes sociais.", REG, 13, 19, INK)
    text(c, M, 340, "RTT", BOLD, 40, BLUE, cs=-0.5)
    text(c, M, 372, "Vulcanização e produtos", REG, 13, INK)

    # mosaico em bleed à direita
    mx = X(4) - GUT / 2
    mw = W - mx
    mh = mw / (1408 / 751)
    my = (H - mh) / 2
    c.drawImage(asset("rtt_mosaic.jpg"), mx, my, width=mw, height=mh)
    c.showPage()


def slide_experience(c, n, client, title, subtitle, logo, logo_box, posts, dark=False):
    bg = INK if dark else PAPER
    fg = white if dark else INK
    accent = CYAN if dark else BLUE
    sub = HexColor("#A9A9A9") if dark else GRAY
    c.setFillColor(bg)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    header(c, "Experiência · " + client, n, fg,
           rule_color=fg)

    # coluna de título
    text(c, M, 92, title, BOLD, 40, fg, cs=-0.8)
    text(c, M, 130, subtitle, REG, 16, accent)

    # logo do cliente (bloco fixo abaixo do cargo)
    lb_w, lb_h = logo_box
    text(c, M, 330, "CLIENTE", BOLD, 7.5, sub, cs=0.8)
    draw_fit_center(c, asset(logo), M + lb_w / 2, 346 + lb_h / 2, lb_w, lb_h)

    # posts em três colunas de 4 colunas do grid (ocupando as colunas 4 a 11)
    pw = (SPAN(8) - 2 * GUT) / 3
    ph = 226
    top = 118
    for i, p in enumerate(posts):
        px = X(4) + i * (pw + GUT)
        tmp = cover_crop(asset(p), pw, ph)
        c.drawImage(tmp, px, ty(top) - ph, width=pw, height=ph)
        os.remove(tmp)
        text(c, px, top + ph + 22, f"{i + 1:02d}", BOLD, 8, sub, cs=0.6)
    rule(c, X(4), X(12) - GUT, top + ph + 34, fg, 0.5)
    c.showPage()


def slide_identity(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    header(c, "Experiência · Identidade visual", 7)

    text(c, M, 92, "Identidade visual", BOLD, 44, INK, cs=-0.8)
    text(c, M, 130, "Designer — Branding", REG, 16, BLUE)

    logos = [
        ("id_carolina.png", "Carolina de Oliveira"),
        ("id_florenza.png", "Florenza"),
        ("id_ambiental.png", "AmbientalizAr"),
        ("id_vovo.png", "Vovó Cléo"),
        ("id_wes.png", "WES Rendering"),
        ("id_cleaning.png", "Cleaning Care"),
        ("quantum_logo.png", "Quantum"),
    ]
    cw = (SPAN(12) - 3 * GUT) / 4
    ch = 150
    tops = [180, 180 + ch + GUT]
    cells = logos + [None]
    for idx, item in enumerate(cells):
        r, col = divmod(idx, 4)
        x = M + col * (cw + GUT)
        top = tops[r]
        if item is None:
            rect(c, x, top, cw, ch, BLUE)
            text(c, x + 18, top + 34, "07", BOLD, 40, white, cs=-0.5)
            text(c, x + 18, top + 62, "identidades visuais", BOLD, 11, white)
            text(c, x + 18, top + 78, "criadas para clientes", REG, 11, white)
            text(c, x + 18, top + 94, "de diferentes segmentos", REG, 11, white)
            continue
        fname, label = item
        c.setStrokeColor(LIGHT_RULE)
        c.setLineWidth(0.6)
        c.rect(x, ty(top) - ch, cw, ch, stroke=1, fill=0)
        draw_fit_center(c, asset(fname), x + cw / 2, top + ch / 2 - 10, cw - 48, ch - 54)
        text(c, x + 14, top + ch - 14, label.upper(), BOLD, 6.5, GRAY, cs=0.6)
    c.showPage()


def slide_web(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    header(c, "Experiência · Web design", 8)

    text(c, M, 92, "Web", BOLD, 58, INK, cs=-1.2)
    text(c, M, 150, "design", BOLD, 58, INK, cs=-1.2)
    text(c, M, 196, "Freelancer", REG, 16, BLUE)
    text(c, M, 216, "Web designer", REG, 13, GRAY)

    frames = ["web_1.png", "web_2.png", "web_3.jpg", "web_4.jpg"]
    fw = (SPAN(8) - 3 * GUT) / 4
    fh = 360
    top = 110
    for i, f in enumerate(frames):
        fx = X(4) + i * (fw + GUT)
        tmp = cover_crop(asset(f), fw, fh)
        c.drawImage(tmp, fx, ty(top) - fh, width=fw, height=fh)
        os.remove(tmp)
        text(c, fx, top + fh + 22, f"{i + 1:02d}", BOLD, 8, GRAY, cs=0.6)
    rule(c, X(4), X(12) - GUT, top + fh + 34, INK, 0.5)
    c.showPage()


def slide_contact(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    header(c, "Contato", 9, rule_end=X(8) - GUT)

    # bloco azul à direita com retrato
    bx = X(8)
    rect(c, bx, 0, W - bx, H, BLUE)
    # mesmo recorte limpo usado na capa, para manter a identidade entre as páginas
    portrait = trim_alpha(asset("cover_portrait.png"))
    pim = Image.open(portrait)
    max_w, max_h = (W - bx) - 24, 470
    s_ = min(max_w / pim.size[0], max_h / pim.size[1])
    pw, ph = pim.size[0] * s_, pim.size[1] * s_
    c.drawImage(portrait, bx + (W - bx - pw) / 2, 0, width=pw, height=ph, mask="auto")

    text(c, M, 92, "Douglas de", BOLD, 60, INK, cs=-1.4)
    text(c, M, 152, "Oliveira", BOLD, 60, INK, cs=-1.4)
    text(c, M, 200, "Designer Gráfico / Web designer", REG, 18, BLUE)

    rows = [
        ("TELEFONE", "(31) 99581-5198"),
        ("E-MAIL", "douglasagoliveira9@gmail.com"),
        ("ENDEREÇO", "Av. Santa Terezinha, 1875 — Belo Horizonte, MG"),
        ("SITE", "douglas-de-oliveira-designer.vercel.app"),
    ]
    top = 270
    cols_w = X(8) - M - GUT * 2
    for label, value in rows:
        rule(c, M, X(8) - GUT, top, INK, 0.7)
        text(c, M, top + 22, label, BOLD, 7.5, GRAY, cs=0.8)
        text(c, M + 110, top + 22, value, BOLD, 15, INK)
        top += 54
    rule(c, M, X(8) - GUT, top, INK, 0.7)
    c.showPage()


def slide_closing(c):
    c.setFillColor(INK)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # fundo: prints de sites, escurecidos para não competir com o texto
    bg = Image.open(asset("bg_screens.jpg")).convert("RGB")
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    fd, tmp = tempfile.mkstemp(suffix=".jpg", dir=tempfile.gettempdir())
    os.close(fd)
    bg.save(tmp, quality=90)
    c.drawImage(tmp, 0, 0, width=W, height=H)
    os.remove(tmp)

    rect(c, 0, 0, W, H, INK, alpha=0.55)
    header(c, "Obrigado", 10, white, rule_color=white)

    size = fit_size("OBRIGADO", BOLD, 210, W - 2 * M)
    text(c, M - 6, 330, "OBRIGADO", BOLD, size, white, cs=-size * 0.02)
    rect(c, M, 350 + size * 0.02, 72, 8, BLUE)

    text(c, M, 470, "Douglas Antônio Gomes de Oliveira", BOLD, 11, white)
    text(c, M, 488, "douglasagoliveira9@gmail.com  ·  (31) 99581-5198", REG, 11, CYAN)
    text_right(c, W - M, 488, "douglas-de-oliveira-designer.vercel.app", REG, 11, white)
    c.showPage()


# ---------------------------------------------------------------- build
def build():
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Portfólio Douglas de Oliveira — Swiss 16:9")
    c.setAuthor("Douglas Antônio Gomes de Oliveira")
    c.setSubject("Portfólio — Designer Gráfico / Web designer")

    slide_cover(c)
    slide_about(c)
    slide_social_showcase(c)
    slide_experience(
        c, 4, "Vovó Cléo", "Freelancer", "Designer Social Media", "vovo_logo.png", (190, 110),
        ["vovo_1.jpg", "vovo_2.jpg", "vovo_3.jpg"], dark=False)
    slide_experience(
        c, 5, "AmbientalizAr", "Freelancer", "Designer Social Media", "amb_logo.png", (230, 110),
        ["amb_1.jpg", "amb_2.jpg", "amb_3.jpg"], dark=True)
    slide_experience(
        c, 6, "Quantum", "Freelancer", "Designer Social Media", "quantum_logo.png", (150, 150),
        ["qtm_1.jpg", "qtm_2.jpg", "qtm_3.jpg"], dark=False)
    slide_identity(c)
    slide_web(c)
    slide_contact(c)
    slide_closing(c)

    c.save()
    print("PDF gerado:", OUT)


if __name__ == "__main__":
    build()
