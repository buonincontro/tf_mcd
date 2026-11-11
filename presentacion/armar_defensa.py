import os, copy
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
REC = os.path.join(AQUI, "recursos"); EDA = os.path.join(RAIZ, "eda", "figuras"); SIM = os.path.join(RAIZ, "simulador", "resultados")
PLANTILLA = os.path.join(AQUI, "plantillas_austral", "templatePPT clases_2025.pptx")
SALIDA = os.path.join(AQUI, "Defensa - Buonincontro - Trabajo Final MCD.pptx"); PREV = os.path.join(AQUI, "vista_previa")
NAVY, NARANJA, GRIS, BLANCO, TINTE, TINTE_N = "172186", "FD8204", "5A5F7A", "FFFFFF", "EEF0FA", "FFF1E0"
FUENTE = "Century Gothic"; DF = "/Applications/Microsoft PowerPoint.app/Contents/Resources/DFonts/"
DPI = 96; avisos = []
def fnt(size, bold=False):
    try: return ImageFont.truetype(DF + ("Century Gothic Bold.ttf" if bold else "Century Gothic.ttf"), int(round(size / 72 * DPI)))
    except Exception: return ImageFont.load_default()
px = lambda v: int(round(v * DPI))

class Lamina:
    def __init__(self, fondo, notas=""): self.fondo, self.notas, self.items = fondo, notas, []
    def texto(self, x, y, w, h, paras, size=18, color=NAVY, bold=False, align="l", anchor="t", gap=6):

        ps = [dict(t=p) if isinstance(p, str) else dict(p) for p in (paras if isinstance(paras, list) else [paras])]
        for p in ps:
            p.setdefault("size", size); p.setdefault("color", color); p.setdefault("bold", bold); p.setdefault("bullet", False); p.setdefault("gap", gap)
        self.items.append(("texto", x, y, w, h, ps, align, anchor)); return self
    def imagen(self, ruta, x, y, w, h): self.items.append(("imagen", x, y, w, h, ruta)); return self
    def caja(self, x, y, w, h, fill=TINTE, radio=True): self.items.append(("caja", x, y, w, h, fill, radio)); return self
    def tabla(self, x, y, anchos, filas, alto=0.5, size=14): self.items.append(("tabla", x, y, anchos, filas, alto, size)); return self
    def titulo(self, t, sub=None):
        self.texto(0.9, 0.42, 10.2, 0.7, t, size=32, bold=True)
        if sub: self.texto(0.9, 1.12, 10.2, 0.45, sub, size=18, color=NARANJA)
        return self

def envolver(d, t, f, ancho):
    lineas = []
    for trozo in t.split("\n"):
        actual = ""
        for palabra in trozo.split(" "):
            prueba = (actual + " " + palabra).strip()
            if d.textlength(prueba, font=f) <= ancho or not actual: actual = prueba
            else: lineas.append(actual); actual = palabra
        lineas.append(actual)
    return lineas
def medir(d, ps, ancho):
    out, total = [], 0
    for p in ps:
        f = fnt(p["size"], p["bold"]); sangria = px(0.28) if p["bullet"] else 0
        ls = envolver(d, p["t"], f, ancho - sangria); alto = p["size"] / 72 * DPI * 1.22
        out.append((p, f, ls, alto, sangria)); total += len(ls) * alto + p["gap"] / 72 * DPI
    return out, total - (ps[-1]["gap"] / 72 * DPI if ps else 0)
def dibujar_texto(d, n, x, y, w, h, ps, align, anchor, etiqueta=""):
    bloques, total = medir(d, ps, px(w))
    if total > px(h) + 2: avisos.append(f"lámina {n}: texto desborda {total / DPI:.2f} > {h:.2f} in: {ps[0]['t'][:40]!r}")
    cy = px(y) + (max(0, (px(h) - total) / 2) if anchor == "m" else 0)
    for p, f, ls, alto, sangria in bloques:
        for i, l in enumerate(ls):
            tw = d.textlength(l, font=f)
            if tw > px(w) - sangria + 2: avisos.append(f"lámina {n}: palabra más ancha que la caja: {l[:30]!r}")
            cx = px(x) + sangria + (0 if align == "l" else (px(w) - sangria - tw) / 2 if align == "c" else px(w) - sangria - tw)
            if p["bullet"] and i == 0: d.text((px(x) + 4, cy), "•", font=f, fill="#" + p["color"])
            d.text((cx, cy), l, font=f, fill="#" + p["color"]); cy += alto
        cy += p["gap"] / 72 * DPI

def encajar(ruta, w, h):
    iw, ih = Image.open(ruta).size; r = min(w / iw, h / ih); return iw * r, ih * r

def construir(laminas):
    prs = Presentation(PLANTILLA)
    lst = prs.slides._sldIdLst
    for sld in list(lst): prs.part.drop_rel(sld.rId); lst.remove(sld)
    layout = prs.slide_layouts[3]; os.makedirs(PREV, exist_ok=True)
    for n, L in enumerate(laminas, 1):
        s = prs.slides.add_slide(layout)
        for ph in list(s.placeholders): ph._element.getparent().remove(ph._element)
        _, rid = s.part.get_or_add_image_part(os.path.join(REC, L.fondo))
        bg = etree.fromstring(f'<p:bg xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:bgPr><a:blipFill dpi="0" rotWithShape="1"><a:blip r:embed="{rid}"/><a:srcRect/><a:stretch><a:fillRect/></a:stretch></a:blipFill><a:effectLst/></p:bgPr></p:bg>')
        s._element.cSld.insert(0, bg)
        im = Image.open(os.path.join(REC, L.fondo)).convert("RGB").resize((px(13.333), px(7.5))); d = ImageDraw.Draw(im, "RGBA")
        for it in L.items:
            if it[0] == "caja":
                _, x, y, w, h, fill, radio = it
                sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radio else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
                if radio: sh.adjustments[0] = min(0.5, 0.12 / min(w, h))
                sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(fill); sh.line.fill.background(); sh.shadow.inherit = False
                d.rounded_rectangle([px(x), px(y), px(x + w), px(y + h)], radius=px(0.12) if radio else 0, fill="#" + fill)
            elif it[0] == "imagen":
                _, x, y, w, h, ruta = it; rw, rh = encajar(ruta, w, h); ox, oy = x + (w - rw) / 2, y + (h - rh) / 2
                pic = s.shapes.add_picture(ruta, Inches(ox), Inches(oy), Inches(rw), Inches(rh)); pic.name = os.path.basename(ruta)
                pi = Image.open(ruta).convert("RGBA").resize((px(rw), px(rh))); im.paste(pi, (px(ox), px(oy)), pi)
            elif it[0] == "texto":
                _, x, y, w, h, ps, align, anchor = it
                tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
                tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
                tf.vertical_anchor = MSO_ANCHOR.MIDDLE if anchor == "m" else MSO_ANCHOR.TOP
                for i, p in enumerate(ps):
                    par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                    par.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]; par.space_after = Pt(p["gap"])
                    for j, linea in enumerate(p["t"].split("\n")):
                        if j: par.add_line_break()
                        r = par.add_run(); r.text = linea; r.font.size = Pt(p["size"]); r.font.bold = p["bold"]; r.font.name = FUENTE; r.font.color.rgb = RGBColor.from_string(p["color"])
                    if p["bullet"]:
                        pPr = par._p.get_or_add_pPr(); pPr.set("marL", str(Inches(0.28))); pPr.set("indent", str(-Inches(0.28)))
                        bu = etree.SubElement(pPr, qn("a:buChar")); bu.set("char", "•")
                dibujar_texto(d, n, x, y, w, h, ps, align, anchor)
            elif it[0] == "tabla":
                _, x, y, anchos, filas, alto, size = it
                gt = s.shapes.add_table(len(filas), len(anchos), Inches(x), Inches(y), Inches(sum(anchos)), Inches(alto * len(filas))); t = gt.table
                for c, a in enumerate(anchos): t.columns[c].width = Inches(a)
                for r, fila in enumerate(filas):
                    t.rows[r].height = Inches(alto)
                    for c, val in enumerate(fila):
                        cel = t.cell(r, c); cel.fill.solid(); cab = r == 0
                        cel.fill.fore_color.rgb = RGBColor.from_string(NAVY if cab else (TINTE if r % 2 else BLANCO))
                        cel.margin_left = cel.margin_right = Inches(0.12); cel.margin_top = cel.margin_bottom = Inches(0.04); cel.vertical_anchor = MSO_ANCHOR.MIDDLE
                        par = cel.text_frame.paragraphs[0]; run = par.add_run(); run.text = val; run.font.size = Pt(size); run.font.name = FUENTE
                        run.font.bold = cab or c == 0; run.font.color.rgb = RGBColor.from_string(BLANCO if cab else NAVY)
                        cx = x + sum(anchos[:c]); cy = y + r * alto
                        d.rectangle([px(cx), px(cy), px(cx + anchos[c]) - 1, px(cy + alto) - 1], fill="#" + (NAVY if cab else (TINTE if r % 2 else BLANCO)))
                        dibujar_texto(d, n, cx + 0.12, cy + 0.04, anchos[c] - 0.24, alto - 0.08, [dict(t=val, size=size, color=BLANCO if cab else NAVY, bold=cab or c == 0, bullet=False, gap=0)], "l", "m")
        if L.notas: s.notes_slide.notes_text_frame.text = L.notas
        im.save(os.path.join(PREV, f"lamina_{n:02d}.png"))
    prs.save(SALIDA)

def tarjeta_dato(L, x, y, w, h, numero, leyenda, fill=TINTE, size=48):
    L.caja(x, y, w, h, fill); L.texto(x + 0.3, y + 0.3, w - 0.6, 1.1, numero, size=size, bold=True, color=NARANJA, anchor="m")
    L.texto(x + 0.3, y + 1.45, w - 0.6, h - 1.65, leyenda, size=16)

exec(open(os.path.join(AQUI, "contenido_defensa.py"), encoding="utf-8").read())
construir(LAMINAS)
print(f"{len(LAMINAS)} láminas ->", os.path.basename(SALIDA)); print("\n".join(avisos) if avisos else "sin desbordes de texto en la vista previa")
