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
2. Créer `contenu/<slug>/` et y placer `source.pdf`. **Flouter ensuite les noms avant toute publication : le site est public.**
   - `python3 outils/noms.py reperer <slug>` liste, page par page, les mots en capitales, les e-mails et les mots à majuscule lus dans les captures.
   - Y relever tout ce qui désigne une personne ou une entreprise réelle : salariés, adhérents, contacts, médecins, collègues, identifiants de connexion, e-mails. Les données de test évidentes (« ENTREPRISE TEST », « Test Médecin ») peuvent rester.
   - `python3 outils/noms.py flouter <slug> nom1 nom2 …` ajoute les zones dans `fiche.json`, qui doit déjà exister : écrire la fiche de l'étape 3 avant cette commande (suffixe `=` pour une correspondance exacte, utile pour les mots courts ou ambigus).
   - Regarder ensuite en image les pages à captures : la reconnaissance rate les textes très petits (rendez-vous d'agenda, lignes de tableau). Compléter à la main dans `masques` (fractions de la page : `[x0, y0, x1, y1]`), en masquant large.
   - Toute information de santé liée à une personne ou à une entreprise identifiable : masquer la zone entière et le signaler à Florent.
   - Ne proposer le PDF d'origine en téléchargement (`pdf_telechargeable: true`) que s'il ne contient aucune donnée de ce type. En cas de doute, publier sans captures (`"captures": false`).
3. Écrire `contenu/<slug>/fiche.json` (voir `contenu/amt-pulse/fiche.json`). Découper en chapitres avec leurs numéros de pages. Rédiger `essentiel` : fidèle au document, étapes numérotées, phrases courtes, vouvoiement, libellés exacts de l'écran entre « ». Ne rien inventer ; ne pas reprendre les notes de travail du rédacteur (« capture à refaire », « lien à afficher »), mais les signaler à Florent.
4. Mise à jour : même slug, remplacer `source.pdf`, incrémenter `version`, changer `date`, renseigner `note`.
5. `python3 outils/construire.py <slug>`, vérifier le rendu, commiter, pousser sur `main`.
6. Passer le dépôt en `statut: "publie"` dans le journal de la page « Dépôt des modes d'emploi » (artifact, collection `depots`).

## Règles
- `"captures": false` dans une fiche publie le document sans ses pages d'origine (cas d'un PDF dont les captures contiennent des données réelles). Remettre à `true` une fois le PDF nettoyé.
- Les `source.pdf` ne sont pas versionnés (`.gitignore`) : le dépôt est public et un PDF peut contenir des données que les masques ne couvrent pas. Pour régénérer les images d'un document, redemander le PDF. Sans `source.pdf`, `construire.py` conserve l'entrée déjà publiée dans `data.js` : on peut donc ajouter un document sans avoir les PDF des autres.
- Charte : vert #60BB46, orange #F37537, rose #EF599A, marine #172F57, bleu #2091D0, police Lato. Pas de violet.
- Le site ne doit pas être indexé (`noindex`, `robots.txt`).
