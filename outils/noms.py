#!/usr/bin/env python3
"""Repère et floute les noms dans les captures d'un PDF (reconnaissance de texte).

1. Lister les candidats, page par page (mots en capitales, e-mails, mots à majuscule) :
     python3 outils/noms.py reperer <slug>
2. Flouter toutes les occurrences des mots choisis (sans tenir compte de la casse ni des accents ;
   un mot suivi de "=" doit correspondre exactement, casse comprise) :
     python3 outils/noms.py flouter <slug> picard marjory "LYONNAIS=" "Luc="
   Les zones s'ajoutent à "masques" dans contenu/<slug>/fiche.json. Relancer ensuite construire.py.

Limite : un nom écrit très petit peut ne pas être reconnu. Toujours contrôler les pages à l'œil après,
et ajouter à la main dans "masques" les zones manquantes ([x0, y0, x1, y1] en fractions de la page).
Outils requis : pdftoppm, tesseract (langue fra), pytesseract, Pillow.
"""
import json, re, subprocess, sys, tempfile, unicodedata
from pathlib import Path
import pytesseract
from PIL import Image

RACINE = Path(__file__).resolve().parent.parent
Image.MAX_IMAGE_PIXELS = None
BORD = " .,:;()[]«»\"'"


def plat(t):
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


def mots_par_page(slug):
    """{page: [[mot, x0, y0, x1, y1], ...]}, coordonnées en fractions de la page. Mis en cache."""
    cache = RACINE / "contenu" / slug / ".mots.json"
    pdf = RACINE / "contenu" / slug / "source.pdf"
    if cache.exists() and cache.stat().st_mtime > pdf.stat().st_mtime:
        return json.loads(cache.read_text(encoding="utf-8"))
    langue = "fra" if "fra" in pytesseract.get_languages() else "eng"
    pages = {}
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", "300", "-png", str(pdf), f"{tmp}/p"], check=True)
        for n, f in enumerate(sorted(Path(tmp).glob("p-*.png")), 1):
            im = Image.open(f)
            L, H = im.size
            d = pytesseract.image_to_data(im, lang=langue, config="--psm 11", output_type=pytesseract.Output.DICT)
            pages[str(n)] = [
                [t.strip(), d["left"][i] / L, d["top"][i] / H, (d["left"][i] + d["width"][i]) / L, (d["top"][i] + d["height"][i]) / H]
                for i, t in enumerate(d["text"]) if len(t.strip()) > 1 and float(d["conf"][i]) >= 20
            ]
    cache.write_text(json.dumps(pages), encoding="utf-8")
    return pages


def reperer(slug):
    for n, mots in mots_par_page(slug).items():
        nets = [m[0].strip(BORD) for m in mots]
        caps = sorted({m for m in nets if re.fullmatch(r"[A-ZÉÈÀÂÊÎÔÛÇ][A-ZÉÈÀÂÊÎÔÛÇ'\-]{2,}", m)})
        mails = sorted({m for m in nets if "@" in m})
        propres = sorted({m for m in nets if re.fullmatch(r"[A-ZÉÈÀÂÊÎÔÛÇ][a-zéèàâêîôûçï\-]{2,}", m)})
        print(f"\n— Page {n}\n  CAPITALES : {' '.join(caps)}\n  E-MAILS   : {' '.join(mails)}\n  Majuscule : {' '.join(propres)}")


def flouter(slug, cibles):
    exacts = {c[:-1] for c in cibles if c.endswith("=")}
    souples = [plat(c) for c in cibles if not c.endswith("=")]
    chemin = RACINE / "contenu" / slug / "fiche.json"
    fiche = json.loads(chemin.read_text(encoding="utf-8"))
    masques = fiche.setdefault("masques", {})
    for n, mots in mots_par_page(slug).items():
        ajout = [
            [round(max(0, x0 - .006), 4), round(max(0, y0 - .003), 4), round(min(1, x1 + .006), 4), round(min(1, y1 + .003), 4)]
            for t, x0, y0, x1, y1 in mots
            if t.strip(BORD) in exacts or any(s in plat(t) for s in souples)
        ]
        if ajout:
            deja = masques.setdefault(n, [])
            deja.extend(z for z in ajout if z not in deja)
            print(f"page {n} : {len(ajout)} zone(s)")
    chemin.write_text(json.dumps(fiche, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "reperer":
        reperer(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "flouter":
        flouter(sys.argv[2], sys.argv[3:])
    else:
        sys.exit(__doc__)
