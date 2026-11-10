# Hub des modes d'emploi ASMT 65

Site statique (GitHub Pages) destiné aux collaborateurs de l'ASMT 65. Aucun build côté GitHub : les fichiers générés sont commités.

## Structure
- `index.html` : l'application (accueil, filtres, recherche, lecture d'un document). Ne contient aucun contenu.
- `data.js` : généré. Catalogue + texte de recherche.
- `docs/<slug>/pNN.webp` : généré. Pages du PDF rendues en images.
- `contenu/<slug>/fiche.json` + `source.pdf` : la source de chaque mode d'emploi.
- `outils/construire.py` : régénère `data.js` et `docs/`.

## Ajouter ou mettre à jour un mode d'emploi
1. Récupérer le PDF joint à la conversation et la consigne (titre, logiciel, thématique, public, nouveau ou mise à jour, note, référence du dépôt).
2. **Contrôler chaque page du PDF en image avant toute publication.** Le site est public. Repérer dans les captures d'écran les noms de salariés, d'adhérents, de contacts, les e-mails et toute information de santé. Les signaler à Florent et les masquer (`masques` dans la fiche, coordonnées en fractions de la page : `[x0, y0, x1, y1]`). Ne proposer le PDF d'origine en téléchargement (`pdf_telechargeable: true`) que s'il ne contient aucune donnée de ce type.
3. Créer `contenu/<slug>/` avec `source.pdf` et `fiche.json` (voir `contenu/amt-pulse/fiche.json`). Découper en chapitres avec leurs numéros de pages. Rédiger `essentiel` : fidèle au document, étapes numérotées, phrases courtes, vouvoiement, libellés exacts de l'écran entre « ». Ne rien inventer ; ne pas reprendre les notes de travail du rédacteur (« capture à refaire », « lien à afficher »), mais les signaler à Florent.
4. Mise à jour : même slug, remplacer `source.pdf`, incrémenter `version`, changer `date`, renseigner `note`.
5. `python3 outils/construire.py <slug>`, vérifier le rendu, commiter, pousser sur `main`.
6. Passer le dépôt en `statut: "publie"` dans le journal de la page « Dépôt des modes d'emploi » (artifact, collection `depots`).

## Règles
- `"captures": false` dans une fiche publie le document sans ses pages d'origine (cas d'un PDF dont les captures contiennent des données réelles). Remettre à `true` une fois le PDF nettoyé.
- Les `source.pdf` ne sont pas versionnés (`.gitignore`) : le dépôt est public et un PDF peut contenir des données que les masques ne couvrent pas. Pour régénérer les images d'un document, redemander le PDF.
- Charte : vert #60BB46, orange #F37537, rose #EF599A, marine #172F57, bleu #2091D0, police Lato. Pas de violet.
- Le site ne doit pas être indexé (`noindex`, `robots.txt`).
