#!/usr/bin/env python3
"""Reconstruit le hub à partir du dossier contenu/.

Pour chaque contenu/<slug>/ (fiche.json + source.pdf) :
  - rend les pages du PDF en images (docs/<slug>/pNN.webp), masques appliqués ;
  - extrait le texte de chaque page pour la recherche ;
puis écrit data.js, lu par index.html.

Usage : python3 outils/construire.py            (tout)
        python3 outils/construire.py <slug>     (ne re-rend que les images de ce document)
Outils requis : pdftoppm, pdftotext (poppler), Pillow.
"""
import html, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter

RACINE = Path(__file__).resolve().parent.parent
CONTENU, DOCS = RACINE / "contenu", RACINE / "docs"
DPI, LARGEUR_MAX = 120, 1400
HAUT, BAS = 0.028, 0.038  # en-tête et pied d'impression du navigateur, retirés


def texte_brut(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def rogner(im):
    """Retire les marges blanches autour du contenu, en gardant un petit bord."""
    fond = Image.new("RGB", im.size, "white")
    boite = ImageChops.difference(im, fond).point(lambda v: 255 if v > 18 else 0).getbbox()
    if not boite:
        return None
    b = 14
    return im.crop((max(0, boite[0] - b), max(0, boite[1] - b), min(im.width, boite[2] + b), min(im.height, boite[3] + b)))


def rendre_pages(slug, fiche, pages):
    sortie = DOCS / slug
    if sortie.exists():
        shutil.rmtree(sortie)
    sortie.mkdir(parents=True)
    pdf = CONTENU / slug / "source.pdf"
    dims = {}
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", str(DPI), "-png", str(pdf), f"{tmp}/p"], check=True)
        rendus = sorted(Path(tmp).glob("p-*.png"))
        for n in pages:
            im = Image.open(rendus[n - 1]).convert("RGB")
            L, H = im.size
            for x0, y0, x1, y1 in fiche.get("masques", {}).get(str(n), []):
                zone = (int(x0 * L), int(y0 * H), int(x1 * L), int(y1 * H))
                im.paste(im.crop(zone).filter(ImageFilter.GaussianBlur(14)), zone)
            im = rogner(im.crop((0, int(HAUT * H), L, int((1 - BAS) * H))))
            if im is None:
                continue
            if im.width > LARGEUR_MAX:
                im = im.resize((LARGEUR_MAX, round(im.height * LARGEUR_MAX / im.width)), Image.LANCZOS)
            im.save(sortie / f"p{n:02d}.webp", "WEBP", quality=82, method=6)
            dims[n] = [im.width, im.height]
    if fiche.get("pdf_telechargeable"):
        shutil.copy(pdf, sortie / "original.pdf")
    return dims


def dims_existantes(slug):
    return {int(f.stem[1:]): list(Image.open(f).size) for f in sorted((DOCS / slug).glob("p*.webp"))}


def textes_pages(slug):
    brut = subprocess.run(["pdftotext", "-layout", str(CONTENU / slug / "source.pdf"), "-"], check=True, capture_output=True, text=True).stdout
    pages = brut.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    propre = []
    for p in pages:
        lignes = [l.strip() for l in p.splitlines()]
        lignes = [l for l in lignes if l and not re.match(r"^(https?://\S+\s+\d+/\d+|\d{2}/\d{2}/\d{4} \d{2}:\d{2}\b.*)$", l)]
        propre.append(re.sub(r"\s+", " ", " ".join(lignes)))
    return propre


def main():
    cible = sys.argv[1] if len(sys.argv) > 1 else None
    docs = []
    # Les source.pdf ne sont pas versionnés : sans PDF, on garde l'entrée déjà publiée dans data.js.
    anciens = {}
    if (RACINE / "data.js").exists():
        brut = (RACINE / "data.js").read_text(encoding="utf-8").strip()
        anciens = {d["slug"]: d for d in json.loads(brut[len("window.HUB="):].rstrip(";"))["docs"]}
    for dossier in sorted(CONTENU.iterdir()):
        if not (dossier / "fiche.json").exists():
            continue
        slug = dossier.name
        if not (dossier / "source.pdf").exists():
            if slug in anciens:
                docs.append(anciens[slug])
                print(f"{slug} : PDF absent, entrée existante conservée")
            else:
                print(f"{slug} : PDF absent et jamais publié, ignoré")
            continue
        fiche = json.loads((dossier / "fiche.json").read_text(encoding="utf-8"))
        pages = sorted({n for c in fiche["chapitres"] for n in c["pages"]})
        if not fiche.get("captures", True):
            if (DOCS / slug).exists():
                shutil.rmtree(DOCS / slug)
            dims = {}
        elif cible in (None, slug) or not (DOCS / slug).exists():
            dims = rendre_pages(slug, fiche, pages)
        else:
            dims = dims_existantes(slug)
        textes = textes_pages(slug)
        chapitres = [{
            "id": c["id"], "titre": c["titre"], "icone": c.get("icone", ""), "essentiel": c["essentiel"],
            "pages": [{"n": n, "l": dims[n][0], "h": dims[n][1]} for n in c["pages"] if n in dims],
            "recherche": (c["titre"] + " " + texte_brut(c["essentiel"]) + " " + " ".join(textes[n - 1] for n in c["pages"] if n <= len(textes))),
        } for c in fiche["chapitres"]]
        docs.append({k: fiche.get(k) for k in ("titre", "icone", "resume", "logiciel", "thematique", "publics", "version", "date", "note")}
                    | {"slug": slug, "pdf": bool(fiche.get("pdf_telechargeable")), "nbPages": len(textes), "chapitres": chapitres})
        print(f"{slug} : {len(chapitres)} chapitres, {len(dims)} images")
    docs.sort(key=lambda d: d["date"], reverse=True)
    (RACINE / "data.js").write_text("window.HUB=" + json.dumps({"docs": docs}, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"data.js : {len(docs)} document(s)")


if __name__ == "__main__":
    main()
