"""
Portfólio de Douglas de Oliveira — estilo da capa "PORTFÓLIO / DESIGN GRÁFICO".

Linguagem visual: fundo azul-marinho com degradê, colagem de peças tingida em azul,
luz azul vibrante à direita, retrato recortado com brilho, tipografia Montserrat
(geométrica), textos em branco e destaques em azul/ciano com degradê.

Formato: 16:9 (960 x 540 pt). 10 páginas.

Uso (a partir da raiz do repositório):
    python3 portfolio/build_portfolio_cover_style.py

Requer: reportlab, pillow, numpy.
Assets em portfolio/assets e fontes em portfolio/fonts (Montserrat, SIL OFL).
"""

import math
import os
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "Portfolio Douglas de Oliveira - Estilo Capa 16x9.pdf")
TMP = tempfile.mkdtemp(prefix="portfolio_")

W, H = 960, 540          # pontos (16:9)
PX = 2                    # pixels por ponto nas imagens de fundo (1920x1080)
TOTAL = 10

# ---------------------------------------------------------------- fontes
FONT_FILES = {
    "Light": "Montserrat_300Light.ttf",
    "Regular": "Montserrat_400Regular.ttf",
    "Medium": "Montserrat_500Medium.ttf",
    "SemiBold": "Montserrat_600SemiBold.ttf",
    "Bold": "Montserrat_700Bold.ttf",
}
for key, fname in FONT_FILES.items():
    pdfmetrics.registerFont(TTFont(f"Mont-{key}", os.path.join(FONTS, fname)))
F_LIGHT, F_REG, F_MED, F_SEMI, F_BOLD = (f"Mont-{k}" for k in FONT_FILES)

# ---------------------------------------------------------------- cores
NAVY = HexColor("#061236")
BLUE_DEEP = HexColor("#123ABE")
BLUE = HexColor("#2F6BFF")
BLUE_LIGHT = HexColor("#5BB8FF")
CYAN = HexColor("#7FE0FF")
SOFT = HexColor("#B7C8EE")
MUTED = HexColor("#8FA6D6")
WHITE = white


def rgb_t(c):
    return (int(c.red * 255), int(c.green * 255), int(c.blue * 255))


# ---------------------------------------------------------------- fundo (imagem)
def _smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def make_background(name, collage=0.55, glow_x=0.76, glow_y=0.42, glow_k=0.6, edge_bar=True):
    """Gera o fundo em JPEG: degradê azul, colagem tingida, luz e vinheta."""
    w, h = W * PX, H * PX
    xs = np.linspace(0, 1, w)[None, :]
    ys = np.linspace(0, 1, h)[:, None]

    c0 = np.array([6, 18, 54], float)     # navy profundo (esquerda/base)
    c1 = np.array([16, 54, 178], float)   # azul médio
    c2 = np.array([36, 98, 255], float)   # azul vibrante (direita)

    g = np.clip(0.75 * xs + 0.12 * (1 - ys), 0, 1)
    base = c0[None, None, :] + (c1 - c0)[None, None, :] * g[..., None]
    s = _smooth(0.62, 1.0, xs)
    base = base + (c2 - base) * s[..., None] * 0.9

    # colagem de peças, tingida em azul e desbotando para a direita
    coll = Image.open(os.path.join(ASSETS, "bg_screens.jpg")).convert("L")
    coll = coll.resize((w, h), Image.LANCZOS)
    lum = np.asarray(coll).astype(float) / 255.0
    dark, light = np.array([4, 14, 52], float), np.array([120, 170, 255], float)
    tinted = dark + (light - dark) * lum[..., None]
    alpha = np.clip((0.88 - xs) / 0.5, 0, 1) * collage
    alpha = np.broadcast_to(alpha, (h, w))[..., None]
    out = base * (1 - alpha) + tinted * alpha

    # luz radial atrás do retrato
    gx, gy = glow_x * w, glow_y * h
    d = np.sqrt((np.arange(w)[None, :] - gx) ** 2 + (np.arange(h)[:, None] - gy) ** 2)
    glow = np.exp(-(d ** 2) / (2 * (0.20 * w) ** 2)) * glow_k
    glow_col = np.array([70, 140, 255], float)
    out = 255 - (255 - out) * (1 - glow[..., None] * glow_col / 255)

    # faixa de luz vertical na borda direita
    if edge_bar:
        bar = _smooth(0.955, 0.958, xs) * (1 - _smooth(0.99, 1.0, xs))
        bar_col = np.array([60, 130, 255], float)
        out = out * (1 - bar[..., None] * 0.9) + bar_col * bar[..., None] * 0.9

    # vinheta suave
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    vign = np.clip(1 - 0.22 * (r - 0.6).clip(0), 0.7, 1)
    out = out * vign[..., None]

    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
    path = os.path.join(TMP, f"bg_{name}.jpg")
    img.save(path, quality=92)
    return path


def make_glow_streak(path_bg):
    """Linha de luz diagonal fina sobre o fundo (apenas capa)."""
    im = Image.open(path_bg).convert("RGBA")
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w, h = im.size
    d.line([(w * 0.58, h * 1.0), (w * 0.98, h * 0.05)], fill=(140, 220, 255, 170), width=3)
    layer = layer.filter(ImageFilter.GaussianBlur(3))
    im = Image.alpha_composite(im, layer).convert("RGB")
    im.save(path_bg, quality=92)
    return path_bg


# ---------------------------------------------------------------- helpers
def ty(top):
    return H - top


def text(c, x, top, s, font=F_REG, size=12, color=WHITE, cs=0.0):
    t = c.beginText(x, ty(top))
    t.setFont(font, size)
    t.setFillColor(color)
    t.setCharSpace(cs)  # sempre explícito (estado de texto vaza entre blocos)
    t.textOut(s)
    c.drawText(t)


def text_right(c, xr, top, s, font=F_REG, size=12, color=WHITE, cs=0.0):
    w = stringWidth(s, font, size) + cs * max(len(s) - 1, 0)
    text(c, xr - w, top, s, font, size, color, cs)


def text_center(c, xc, top, s, font=F_REG, size=12, color=WHITE, cs=0.0):
    w = stringWidth(s, font, size) + cs * max(len(s) - 1, 0)
    text(c, xc - w / 2, top, s, font, size, color, cs)


def fit_tracking(s, font, size, width):
    """Espaçamento entre letras para que a string ocupe exatamente `width`."""
    base = stringWidth(s, font, size)
    n = max(len(s) - 1, 1)
    return (width - base) / n


def paragraph(c, x, top, width, s, font=F_REG, size=12, leading=None, color=SOFT):
    leading = leading or size * 1.5
    for ln in simpleSplit(s, font, size, width):
        text(c, x, top, ln, font, size, color)
        top += leading
    return top


def hline(c, x1, x2, top, color=WHITE, alpha=0.22, width=0.6):
    c.setStrokeColor(color)
    c.setStrokeAlpha(alpha)
    c.setLineWidth(width)
    c.line(x1, ty(top), x2, ty(top))
    c.setStrokeAlpha(1)


def page_bg(c, bg_path):
    c.drawImage(bg_path, 0, 0, width=W, height=H)


def header(c, section, n):
    text(c, 48, 34, section.upper(), F_MED, 7.5, BLUE_LIGHT, cs=1.6)
    text_right(c, W - 48, 34, f"{n:02d} / {TOTAL:02d}", F_MED, 7.5, SOFT, cs=1.2)


def arrow_down(c, x, top, length=18, color=WHITE):
    c.setStrokeColor(color)
    c.setLineWidth(1.2)
    c.line(x, ty(top), x, ty(top + length))
    c.line(x - 5, ty(top + length - 5), x, ty(top + length))
    c.line(x + 5, ty(top + length - 5), x, ty(top + length))


def gradient_text(c, x, top, s, font, size, color1, color2, cs=0.0, width=None):
    """Texto com degradê horizontal (rasterizado em alta resolução e desenhado como imagem)."""
    if width is not None:
        cs = fit_tracking(s, font, size, width)
    w = stringWidth(s, font, size) + cs * max(len(s) - 1, 0)
    return _gradient_text_image(c, x, top, s, font, size, color1, color2, cs, w)


def _gradient_text_image(c, x, top, s, font, size, color1, color2, cs, w):
    scale = 4
    fnt_path = None
    for key, fname in FONT_FILES.items():
        if f"Mont-{key}" == font:
            fnt_path = os.path.join(FONTS, fname)
    from PIL import ImageFont
    pil_font = ImageFont.truetype(fnt_path, int(size * scale))
    asc, desc = pil_font.getmetrics()
    hpx = asc + desc
    wpx = int(w * scale) + 4
    mask = Image.new("L", (wpx, hpx), 0)
    md = ImageDraw.Draw(mask)
    cx = 0.0
    for ch in s:
        md.text((cx, 0), ch, font=pil_font, fill=255)
        cx += pil_font.getlength(ch) + cs * scale
    # gradiente horizontal
    grad = np.zeros((hpx, wpx, 4), np.uint8)
    c1, c2 = np.array(rgb_t(color1)), np.array(rgb_t(color2))
    t_ = np.linspace(0, 1, wpx)[None, :, None]
    rgb = c1 + (c2 - c1) * t_
    grad[..., :3] = np.broadcast_to(rgb, (hpx, wpx, 3))
    grad[..., 3] = np.asarray(mask)
    img = Image.fromarray(grad, "RGBA")
    p = os.path.join(TMP, f"gt_{abs(hash((s, font, size, rgb_t(color1)))) % 10**8}.png")
    img.save(p)
    # descer da linha de base do PIL (ascender) até a linha de base do PDF
    base_pt = asc / scale
    c.drawImage(p, x, ty(top) - (hpx / scale - base_pt), width=wpx / scale, height=hpx / scale, mask="auto")
    return w


def card(src, w, h, radius=8, glow=True, anchor=(0.5, 0.0), contain=False, bg=None):
    """Imagem com cantos arredondados e halo azul. Retorna (caminho, margem_pt)."""
    S = 3
    margin = 16 if glow else 0
    W_, H_ = int(w * S), int(h * S)
    P = int(margin * S)
    im = Image.open(src).convert("RGBA")
    if contain:
        im.thumbnail((W_ - 2 * int(10 * S), H_ - 2 * int(10 * S)), Image.LANCZOS)
        canvas_im = Image.new("RGBA", (W_, H_), bg or (0, 0, 0, 0))
        canvas_im.alpha_composite(im, ((W_ - im.width) // 2, (H_ - im.height) // 2))
        im = canvas_im
    else:
        iw, ih = im.size
        target = W_ / H_
        if iw / ih > target:
            nw = int(ih * target)
            left = int((iw - nw) * anchor[0])
            im = im.crop((left, 0, left + nw, ih))
        else:
            nh = int(iw / target)
            top = int((ih - nh) * anchor[1])
            im = im.crop((0, top, iw, top + nh))
        im = im.resize((W_, H_), Image.LANCZOS)
    mask = Image.new("L", (W_, H_), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W_ - 1, H_ - 1], radius=int(radius * S), fill=255)
    out = Image.new("RGBA", (W_ + 2 * P, H_ + 2 * P), (0, 0, 0, 0))
    if glow:
        halo = Image.new("RGBA", out.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo)
        hd.rounded_rectangle([P, P, P + W_, P + H_], radius=int(radius * S), fill=(47, 107, 255, 200))
        halo = halo.filter(ImageFilter.GaussianBlur(P * 0.45))
        out = Image.alpha_composite(out, halo)
    body = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    body.paste(im, (0, 0), mask)
    out.alpha_composite(body, (P, P))
    p = os.path.join(TMP, f"card_{abs(hash((src, w, h, radius, glow, anchor))) % 10**9}.png")
    out.save(p)
    return p, margin


def draw_card(c, src, x, top, w, h, radius=8, glow=True, anchor=(0.5, 0.0), contain=False, bg=None):
    p, m = card(src, w, h, radius, glow, anchor, contain, bg)
    c.drawImage(p, x - m, ty(top) - h - m, width=w + 2 * m, height=h + 2 * m, mask="auto")


def logo_tile(c, src, x, top, w, h, pad=18, radius=10):
    """Logo centralizado em cartão branco arredondado (legível em fundo escuro)."""
    S = 3
    W_, H_ = int(w * S), int(h * S)
    tile = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    mask = Image.new("L", (W_, H_), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W_ - 1, H_ - 1], radius=int(radius * S), fill=255)
    base = Image.new("RGBA", (W_, H_), (250, 251, 255, 255))
    tile.paste(base, (0, 0), mask)
    logo = Image.open(src).convert("RGBA")
    maxw, maxh = int((w - 2 * pad) * S), int((h - 2 * pad) * S)
    logo.thumbnail((maxw, maxh), Image.LANCZOS)
    tile.alpha_composite(logo, ((W_ - logo.width) // 2, (H_ - logo.height) // 2))
    p = os.path.join(TMP, f"logo_{abs(hash((src, w, h))) % 10**9}.png")
    tile.save(p)
    c.drawImage(p, x, ty(top) - h, width=w, height=h, mask="auto")


def portrait_bottom(c, src, cx, height, bottom=0):
    """Retrato recortado ancorado na base da página, centralizado em cx."""
    im = Image.open(src).convert("RGBA")
    # remove a semitransparência residual das bordas (evita retângulo/halo cinza)
    a = im.getchannel("A").point(lambda v: min(255, max(0, (v - 60) * 2)))
    im.putalpha(a)
    bbox = a.getbbox()
    if bbox:
        im = im.crop(bbox)
    ratio = im.size[0] / im.size[1]
    w = height * ratio
    p = os.path.join(TMP, "portrait_trim.png")
    im.save(p)
    c.drawImage(p, cx - w / 2, bottom, width=w, height=height, mask="auto")
    return w


def draw_gradient_rect(c, x, top, w, h, color1, color2, radius=0):
    """Retângulo com degradê linear horizontal."""
    c.saveState()
    path = c.beginPath()
    if radius:
        path.roundRect(x, ty(top) - h, w, h, radius)
    else:
        path.rect(x, ty(top) - h, w, h)
    c.clipPath(path, stroke=0, fill=0)
    c.linearGradient(x, 0, x + w, 0, [color1, color2], [0, 1])
    c.restoreState()


def progress_bar(c, x, top, w, h, pct):
    # trilho translúcido
    c.setFillColor(WHITE)
    c.setFillAlpha(0.12)
    c.roundRect(x, ty(top) - h, w, h, h / 2, stroke=0, fill=1)
    c.setFillAlpha(1)
    draw_gradient_rect(c, x, top, w * pct / 100, h, BLUE, CYAN, radius=h / 2)


# ---------------------------------------------------------------- slides
def slide_cover(c, bg):
    page_bg(c, bg)
    # PORTFÓLIO (regular) e DESIGN GRÁFICO (degradê), mesma largura
    x0, width = 85, 315
    s1 = "PORTFÓLIO"
    size1 = width / (stringWidth(s1, F_REG, 1) + 0.06 * (len(s1) - 1))  # tracking leve de 0,06 em
    tr = 0.06 * size1
    text(c, x0, 380, s1, F_REG, size1, WHITE, cs=tr)
    gradient_text(c, x0, 422, "DESIGN GRÁFICO", F_MED, 26, BLUE_LIGHT, CYAN, width=width)
    # seta
    arrow_down(c, 92, 502, 16, SOFT)
    # retrato com halo
    portrait_bottom(c, os.path.join(ASSETS, "cover_portrait.png"), 742, 500)
    # selo circular no canto inferior direito
    cx, cy, r = 894, 466, 44
    c.setStrokeColor(WHITE)
    c.setStrokeAlpha(0.7)
    c.setLineWidth(0.8)
    c.circle(cx, ty(cy), r - 12, stroke=1, fill=0)
    c.setStrokeAlpha(1)
    c.setFillColor(BLUE_LIGHT)
    c.circle(cx, ty(cy), 3, stroke=0, fill=1)
    ring = "PORTFÓLIO • PORTFÓLIO • "
    n = len(ring)
    rad = r - 5
    for i, ch in enumerate(ring):
        ang = 90 - i * (360 / n)  # sentido horário a partir do topo
        a = math.radians(ang)
        px_, py_ = cx + rad * math.cos(a), ty(cy) + rad * math.sin(a)
        c.saveState()
        c.translate(px_, py_)
        c.rotate(ang - 90)
        c.setFillColor(WHITE)
        c.setFont(F_MED, 5.6)
        c.drawCentredString(0, 0, ch)
        c.restoreState()
    c.showPage()


def slide_about(c, bg):
    page_bg(c, bg)
    header(c, "Sobre", 2)
    text(c, 48, 98, "Formação", F_SEMI, 40, WHITE, cs=-0.4)
    text(c, 48, 142, "e habilidades", F_LIGHT, 40, CYAN, cs=-0.4)

    lx, lw = 48, 380
    text(c, lx, 218, "FORMAÇÃO", F_MED, 7.5, BLUE_LIGHT, cs=1.6)
    entries = [
        ("2026", "Publicidade e Propaganda", "Universidade Federal de Minas Gerais (UFMG)"),
        ("2022", "Designer Gráfico", "Escola Casa"),
        ("2018", "Editor de vídeo / Motion Graphic", "Ozi Escola de Audiovisual"),
    ]
    top = 236
    for year, title, inst in entries:
        hline(c, lx, lx + lw, top)
        text(c, lx, top + 40, year, F_SEMI, 26, CYAN)
        text(c, lx + 92, top + 30, title, F_SEMI, 14, WHITE)
        text(c, lx + 92, top + 50, inst, F_REG, 10, SOFT)
        top += 84
    hline(c, lx, lx + lw, top)

    rx, rw = 500, 412
    text(c, rx, 218, "HABILIDADES", F_MED, 7.5, BLUE_LIGHT, cs=1.6)
    skills = [("Design gráfico", 90), ("Edição de vídeo", 80), ("Webdesign", 80)]
    top = 236
    for name, pct in skills:
        hline(c, rx, rx + rw, top)
        text(c, rx, top + 32, name, F_SEMI, 14, WHITE)
        text_right(c, rx + rw, top + 36, f"{pct}%", F_SEMI, 26, CYAN)
        progress_bar(c, rx, top + 54, rw, 7, pct)
        top += 84
    hline(c, rx, rx + rw, top)
    c.showPage()


def slide_social(c, bg):
    page_bg(c, bg)
    header(c, "Experiência · Social media", 3)
    text(c, 48, 98, "Social", F_SEMI, 44, WHITE, cs=-0.6)
    text(c, 48, 146, "media", F_LIGHT, 44, CYAN, cs=-0.6)
    paragraph(c, 48, 206, 250,
              "Peças de campanha para a RTT: promoções, datas comemorativas e "
              "divulgação de produtos para redes sociais.", F_REG, 11.5, 17, SOFT)
    text(c, 48, 336, "RTT", F_BOLD, 30, WHITE, cs=0.5)
    text(c, 48, 360, "Vulcanização e produtos", F_REG, 10.5, BLUE_LIGHT)
    mw = 540
    mh = mw / (1408 / 751)
    draw_card(c, os.path.join(ASSETS, "rtt_mosaic.jpg"), 372, (H - mh) / 2 + 0, mw, mh, radius=10)
    c.showPage()


def slide_experience(c, bg, n, client, logo, logo_kind, posts):
    page_bg(c, bg)
    header(c, "Experiência · " + client, n)
    text(c, 48, 98, "Freelancer", F_SEMI, 38, WHITE, cs=-0.5)
    text(c, 48, 134, "Designer Social Media", F_MED, 14, BLUE_LIGHT)
    text(c, 48, 352, "CLIENTE", F_MED, 7.5, SOFT, cs=1.6)
    if logo_kind == "tile":
        logo_tile(c, os.path.join(ASSETS, logo), 48, 410, 210, 118, pad=8)
    else:
        # logos claros/transparentes: diretamente sobre o fundo
        p = os.path.join(ASSETS, logo)
        im = Image.open(p)
        lw_ = 170
        lh_ = lw_ / (im.size[0] / im.size[1])
        c.drawImage(p, 48, ty(368) - lh_, width=lw_, height=lh_, mask="auto")

    pw, ph = 178, 232
    gap = (570 - 3 * pw) / 2
    for i, pst in enumerate(posts):
        x = 336 + i * (pw + gap)
        draw_card(c, os.path.join(ASSETS, pst), x, 110, pw, ph, radius=8, anchor=(0.5, 0.0))
        text(c, x, 110 + ph + 30, f"{i + 1:02d}", F_MED, 8, BLUE_LIGHT, cs=1.2)
    c.showPage()


def slide_identity(c, bg):
    page_bg(c, bg)
    header(c, "Experiência · Identidade visual", 7)
    text(c, 48, 98, "Identidade visual", F_SEMI, 36, WHITE, cs=-0.5)
    text(c, 48, 130, "Designer — Branding", F_MED, 14, BLUE_LIGHT)

    logos = [
        ("id_carolina.png", "Carolina de Oliveira"),
        ("id_florenza.png", "Florenza"),
        ("id_ambiental.png", "AmbientalizAr"),
        ("id_vovo.png", "Vovó Cléo"),
        ("id_wes.png", "WES Rendering"),
        ("id_cleaning.png", "Cleaning Care"),
        ("quantum_logo.png", "Quantum"),
    ]
    gap = 14
    cw = (864 - 3 * gap) / 4
    ch = 152
    tops = [180, 180 + ch + gap]
    for idx in range(8):
        r, col = divmod(idx, 4)
        x = 48 + col * (cw + gap)
        top = tops[r]
        if idx == 7:
            draw_gradient_rect(c, x, top, cw, ch, BLUE, BLUE_LIGHT, radius=10)
            text(c, x + 20, top + 52, "07", F_BOLD, 38, WHITE)
            text(c, x + 20, top + 80, "identidades visuais", F_SEMI, 11, WHITE)
            text(c, x + 20, top + 96, "para clientes de", F_REG, 10, WHITE)
            text(c, x + 20, top + 110, "diferentes segmentos", F_REG, 10, WHITE)
            continue
        fname, label = logos[idx]
        logo_tile(c, os.path.join(ASSETS, fname), x, top, cw, ch - 26, pad=22)
        text(c, x + 2, top + ch - 6, label.upper(), F_MED, 6.5, MUTED, cs=1.0)
    c.showPage()


def slide_web(c, bg):
    page_bg(c, bg)
    header(c, "Experiência · Web design", 8)
    text(c, 48, 98, "Web design", F_SEMI, 38, WHITE, cs=-0.5)
    text(c, 48, 134, "Freelancer", F_MED, 14, BLUE_LIGHT)
    text(c, 48, 156, "Web designer", F_REG, 11, SOFT)
    frames = ["web_1.png", "web_2.png", "web_3.jpg", "web_4.jpg"]
    gap = 12
    fw = (570 - 3 * gap) / 4
    fh = 360
    for i, f in enumerate(frames):
        x = 336 + i * (fw + gap)
        draw_card(c, os.path.join(ASSETS, f), x, 110, fw, fh, radius=8, anchor=(0.5, 0.0))
        text(c, x, 110 + fh + 30, f"{i + 1:02d}", F_MED, 8, BLUE_LIGHT, cs=1.2)
    c.showPage()


def slide_contact(c, bg):
    page_bg(c, bg)
    header(c, "Contato", 9)
    text(c, 48, 98, "Douglas de", F_SEMI, 46, WHITE, cs=-0.6)
    text(c, 48, 150, "Oliveira", F_LIGHT, 46, CYAN, cs=-0.6)
    text(c, 48, 186, "Designer Gráfico / Web designer", F_MED, 14, BLUE_LIGHT)
    rows = [
        ("TELEFONE", "(31) 99581-5198"),
        ("E-MAIL", "douglasagoliveira9@gmail.com"),
        ("ENDEREÇO", "Av. Santa Terezinha, 1875 — Belo Horizonte, MG"),
        ("SITE", "douglas-de-oliveira-designer.vercel.app"),
    ]
    top = 248
    for label, value in rows:
        hline(c, 48, 500, top)
        text(c, 48, top + 28, label, F_MED, 7, BLUE_LIGHT, cs=1.6)
        text(c, 160, top + 30, value, F_SEMI, 13, WHITE)
        top += 60
    hline(c, 48, 500, top)
    portrait_bottom(c, os.path.join(ASSETS, "cover_portrait.png"), 742, 520)
    c.showPage()


def slide_closing(c, bg):
    page_bg(c, bg)
    header(c, "Obrigado", 10)
    size = 118
    s = "OBRIGADO"
    width = 800
    tr = fit_tracking(s, F_BOLD, size, width)
    gradient_text(c, 48, 330, s, F_BOLD, size, WHITE, CYAN, cs=tr)
    draw_gradient_rect(c, 48, 352, 84, 4, BLUE, CYAN, radius=2)
    text(c, 48, 462, "Douglas Antônio Gomes de Oliveira", F_SEMI, 12, WHITE)
    text(c, 48, 480, "douglasagoliveira9@gmail.com  ·  (31) 99581-5198", F_REG, 11, CYAN)
    text_right(c, W - 48, 480, "douglas-de-oliveira-designer.vercel.app", F_REG, 11, SOFT)
    c.showPage()


# ---------------------------------------------------------------- build
def build():
    bg_cover = make_glow_streak(make_background("cover", collage=0.6, glow_x=0.76, glow_y=0.42, glow_k=0.7))
    bg_content = make_background("content", collage=0.32, glow_x=0.95, glow_y=0.2, glow_k=0.45)
    bg_close = make_background("close", collage=0.5, glow_x=0.5, glow_y=0.35, glow_k=0.55, edge_bar=True)

    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Portfólio Douglas de Oliveira — Estilo Capa")
    c.setAuthor("Douglas Antônio Gomes de Oliveira")
    c.setSubject("Portfólio — Designer Gráfico / Web designer")

    slide_cover(c, bg_cover)
    slide_about(c, bg_content)
    slide_social(c, bg_content)
    slide_experience(c, bg_content, 4, "Vovó Cléo", "vovo_logo.png", "bare",
                     ["vovo_1.jpg", "vovo_2.jpg", "vovo_3.jpg"])
    slide_experience(c, bg_content, 5, "AmbientalizAr", "amb_logo.png", "bare",
                     ["amb_1.jpg", "amb_2.jpg", "amb_3.jpg"])
    slide_experience(c, bg_content, 6, "Quantum", "quantum_logo.png", "tile",
                     ["qtm_1.jpg", "qtm_2.jpg", "qtm_3.jpg"])
    slide_identity(c, bg_content)
    slide_web(c, bg_content)
    slide_contact(c, bg_content)
    slide_closing(c, bg_close)

    c.save()
    print("PDF gerado:", OUT)


if __name__ == "__main__":
    build()
