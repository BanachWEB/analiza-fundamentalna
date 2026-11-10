"""Markdown (podzbiór) → PDF w ReportLab z czcionką DejaVu (polskie znaki).

Obsługa: nagłówki #–###, akapity, listy „- ” i „1. ”, tabele z kreskami, obrazy ![](plik),
cytaty „> ”, linia pozioma, **pogrubienie**, *kursywa*, `kod`, przypisy [^n].
"""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (HRFlowable, Image, KeepTogether, ListFlowable, ListItem, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

KATALOG_CZCIONEK = Path(os.path.dirname(matplotlib.__file__)) / "mpl-data" / "fonts" / "ttf"
for nazwa, plik in (("DejaVu", "DejaVuSans.ttf"), ("DejaVu-Bold", "DejaVuSans-Bold.ttf"),
                    ("DejaVu-Oblique", "DejaVuSans-Oblique.ttf"), ("DejaVu-BoldOblique", "DejaVuSans-BoldOblique.ttf"),
                    ("DejaVuMono", "DejaVuSansMono.ttf")):
    pdfmetrics.registerFont(TTFont(nazwa, str(KATALOG_CZCIONEK / plik)))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold", italic="DejaVu-Oblique",
                              boldItalic="DejaVu-BoldOblique")

TEKST, TEKST2, LINIA, AKCENT, TLO_TAB = (colors.HexColor(x) for x in ("#0b0b0b", "#52514e", "#d9d8d3", "#2a78d6", "#f4f3f0"))
S = {
    "h1": ParagraphStyle("h1", fontName="DejaVu-Bold", fontSize=17, leading=21, spaceAfter=6, textColor=TEKST),
    "h2": ParagraphStyle("h2", fontName="DejaVu-Bold", fontSize=12.5, leading=16, spaceBefore=10, spaceAfter=4, textColor=TEKST),
    "h3": ParagraphStyle("h3", fontName="DejaVu-Bold", fontSize=10.5, leading=14, spaceBefore=6, spaceAfter=2, textColor=TEKST),
    "p": ParagraphStyle("p", fontName="DejaVu", fontSize=9, leading=12.6, spaceAfter=4, textColor=TEKST, alignment=TA_LEFT),
    "cytat": ParagraphStyle("cytat", fontName="DejaVu", fontSize=9, leading=12.6, textColor=TEKST, backColor=TLO_TAB,
                            borderPadding=6, leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=8),
    "tab": ParagraphStyle("tab", fontName="DejaVu", fontSize=7.4, leading=9.2, textColor=TEKST),
    "tab_b": ParagraphStyle("tab_b", fontName="DejaVu-Bold", fontSize=7.4, leading=9.2, textColor=TEKST),
    "przypis": ParagraphStyle("przypis", fontName="DejaVu", fontSize=6.8, leading=8.6, textColor=TEKST2, spaceAfter=1.5),
}


def _inline(t: str) -> str:
    t = escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<i>\1</i>", t)
    t = re.sub(r"`([^`]+)`", r'<font name="DejaVuMono">\1</font>', t)
    t = re.sub(r"\[\^(\d+)\]", r'<super><font color="#2a78d6" size="6">\1</font></super>', t)
    return t


def _tabela(wiersze: list[str], szerokosc: float):
    komorki = [[c.strip() for c in w.strip().strip("|").split("|")] for w in wiersze
               if not re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?", w.strip())]
    if not komorki:
        return None
    n = max(len(r) for r in komorki)
    dane = [[Paragraph(_inline(c), S["tab_b"] if i == 0 else S["tab"]) for c in r + [""] * (n - len(r))]
            for i, r in enumerate(komorki)]
    # szerokości proporcjonalne do najdłuższego tekstu w kolumnie (z granicami), żeby opisy nie łamały się co słowo
    dlugosci = []
    for j in range(n):
        teksty = [re.sub(r"<[^>]+>", "", r[j]) if j < len(r) else "" for r in komorki]
        dlugosci.append(min(55, max(5, max(len(t) for t in teksty))))
    suma = sum(dlugosci)
    t = Table(dane, colWidths=[szerokosc * d / suma for d in dlugosci], repeatRows=1)
    t.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, TEKST2), ("LINEBELOW", (0, 1), (-1, -1), 0.3, LINIA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def zbuduj(md: str, wyjscie: Path, tytul: str, katalog_obrazow: Path) -> Path:
    szer = A4[0] - 36 * mm
    elementy = []
    linie = md.splitlines()
    i = 0
    przypisy = []
    while i < len(linie):
        l = linie[i]
        if not l.strip():
            i += 1
            continue
        if l.startswith("[^"):
            przypisy.append(l)
            i += 1
            continue
        if l.startswith("|"):
            blok = []
            while i < len(linie) and linie[i].startswith("|"):
                blok.append(linie[i])
                i += 1
            t = _tabela(blok, szer)
            if t:
                elementy += [t, Spacer(1, 5)]
            continue
        m = re.match(r"^(#{1,3})\s+(.*)", l)
        if m:
            poziom = len(m.group(1))
            if poziom == 2 and m.group(2).startswith("Przypisy"):
                i += 1
                continue
            elementy.append(Paragraph(_inline(m.group(2)), S[f"h{poziom}"]))
            if poziom == 1:
                elementy.append(HRFlowable(width="100%", thickness=1.2, color=AKCENT, spaceAfter=6))
            i += 1
            continue
        m = re.match(r"^!\[[^\]]*\]\(([^)]+)\)", l.strip())
        if m:
            p = katalog_obrazow / m.group(1)
            if p.exists():
                from reportlab.lib.utils import ImageReader
                w, h = ImageReader(str(p)).getSize()
                elementy += [Image(str(p), width=szer, height=szer * h / w), Spacer(1, 4)]
            i += 1
            continue
        if l.strip() in ("---", "***"):
            elementy.append(HRFlowable(width="100%", thickness=0.5, color=LINIA, spaceBefore=4, spaceAfter=4))
            i += 1
            continue
        if l.startswith(">"):
            blok = []
            while i < len(linie) and linie[i].startswith(">"):
                blok.append(linie[i].lstrip("> ").rstrip())
                i += 1
            elementy.append(Paragraph(_inline(" ".join(blok)), S["cytat"]))
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", l)
        if m:
            numerowana = m.group(2)[0].isdigit()
            punkty = []
            while i < len(linie):
                mm_ = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", linie[i])
                if not mm_:
                    break
                punkty.append(ListItem(Paragraph(_inline(mm_.group(3)), S["p"]), leftIndent=12))
                i += 1
            elementy.append(ListFlowable(punkty, bulletType="1" if numerowana else "bullet", start="1" if numerowana else None,
                                         bulletFontName="DejaVu", bulletFontSize=8, leftIndent=12))
            continue
        akapit = [l.strip()]
        i += 1
        while i < len(linie) and linie[i].strip() and not re.match(r"^(#|\||>|!\[|\[\^|\s*([-*]|\d+\.)\s)", linie[i]):
            akapit.append(linie[i].strip())
            i += 1
        elementy.append(Paragraph(_inline(" ".join(akapit)), S["p"]))

    if przypisy:
        elementy += [Spacer(1, 8), Paragraph("Przypisy: źródła liczb", S["h2"])]
        for p in przypisy:
            m = re.match(r"\[\^(\d+)\]:\s*(.*)", p)
            if m:
                elementy.append(Paragraph(f"<b>{m.group(1)}.</b> " + _inline(m.group(2)), S["przypis"]))

    def stopka(c, doc):
        c.saveState()
        c.setFont("DejaVu", 7)
        c.setFillColor(TEKST2)
        c.drawString(18 * mm, 10 * mm, f"{tytul} · wygenerowano {date.today().isoformat()} · liczby z rejestru faktów, źródła w przypisach")
        c.drawRightString(A4[0] - 18 * mm, 10 * mm, f"strona {doc.page}")
        c.restoreState()

    doc = SimpleDocTemplate(str(wyjscie), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm,
                            bottomMargin=18 * mm, title=tytul, author="analiza-fundamentalna")
    doc.build(elementy, onFirstPage=stopka, onLaterPages=stopka)
    return wyjscie
