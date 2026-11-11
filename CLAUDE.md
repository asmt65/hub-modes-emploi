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
3. Écrire `contenu/<slug>/fiche.json` (voir `contenu/amt-pulse/fiche.json`). Découper en chapitres avec leurs numéros de pages. Rédiger `essentiel` selon la section « Rédiger la synthèse » ci-dessous : fidèle au document, étapes numérotées, phrases courtes, vouvoiement, libellés exacts de l'écran entre « ». Ne rien inventer ; ne pas reprendre les notes de travail du rédacteur (« capture à refaire », « lien à afficher »), mais les signaler à Florent.
4. Mise à jour : même slug, remplacer `source.pdf`, incrémenter `version`, changer `date`, renseigner `note`.
5. `python3 outils/construire.py <slug>`, vérifier le rendu, commiter, pousser sur `main`.
6. Passer le dépôt en `statut: "publie"` dans le journal de la page « Dépôt des modes d'emploi » (artifact, collection `depots`).

## Rédiger la synthèse : utile avant tout
Le lecteur est un collaborateur devant son écran, qui veut faire quelque chose maintenant. La synthèse n'est pas un résumé du PDF : c'est ce qu'il lui faut pour y arriver.

- **Découper par tâche, pas par chapitre du PDF.** Un titre d'étape répond à « je veux… » : « Créer une demande d'intervention », pas « Chapitre IV ». Fusionner les chapitres trop minces, scinder ceux qui couvrent plusieurs tâches. Viser 4 à 10 étapes par document.
- **Supprimer ce qui ne sert pas à agir** : introductions, généralités, descriptions d'écran sans action, ce que tout utilisateur sait déjà. Une étape sans action ni information utile ne mérite pas d'exister.
- **Commencer par le geste.** Étapes numérotées, un geste par ligne, le libellé exact du bouton entre « ». Le contexte vient après, en une phrase, seulement s'il change ce que fait le lecteur.
- **Faire ressortir les pièges et les règles maison** (encadré `alerte`) : cases cochées par défaut, champs à remplir en premier, valeurs imposées à l'ASMT, erreurs fréquentes. C'est souvent la partie la plus utile du document.
- **Dire ce qui n'est pas utilisé à l'ASMT** en une ligne, pour éviter au lecteur de chercher.
- **Rester court.** Une étape se lit en moins d'une minute : 3 à 8 lignes d'action, 2 encadrés au plus. Si c'est plus long, l'étape couvre deux tâches.
- **Ne rien inventer, ne rien deviner.** Si le PDF est flou ou incomplet sur un point, ne pas combler : le signaler à Florent.
- **Les captures servent de preuve, pas de contenu.** Le lecteur doit pouvoir réussir avec le texte seul.
- Avant de publier, relire chaque étape avec une question : « un collègue qui n'a jamais fait cette manipulation y arrive-t-il avec ça ? »

## Règles
- Recherche : sans accents, tolérante aux fautes de frappe, triée par pertinence. Les synonymes et abréviations maison sont dans la constante `SYNONYMES` de `index.html` (un groupe de termes équivalents par ligne, sans accents) ; la compléter quand Florent signale un terme que les collaborateurs utilisent.
- `"captures": false` dans une fiche publie le document sans ses pages d'origine (cas d'un PDF dont les captures contiennent des données réelles). Remettre à `true` une fois le PDF nettoyé.
- Les `source.pdf` ne sont pas versionnés (`.gitignore`) : le dépôt est public et un PDF peut contenir des données que les masques ne couvrent pas. Pour régénérer les images d'un document, redemander le PDF. Sans `source.pdf`, `construire.py` conserve l'entrée déjà publiée dans `data.js` : on peut donc ajouter un document sans avoir les PDF des autres.
- Identité visuelle et ton : ceux de l'extranet ASMT (choix de Florent). Fond bleu nuit presque uni (variante sobre de l'extranet, validée par Florent), cartes blanches très arrondies, accents en dégradé rose #EF599A → orange #F37537, bleu #2091D0, police Lato, titres de carte en capitales bicolores avec épingle et soulignement pointillé, listes à puces bleues. Libellés simples et directs, comme sur l'extranet (« Rechercher un mode d'emploi », « Toutes les étapes », « [NOUVEAU] », « Ajouté le… »). Documents et étapes présentés en cartes avec un émoji (champ `icone` de la fiche, un par document et par étape, choisi pour évoquer la tâche). Pas de slogans, pas de violet.
- Le site ne doit pas être indexé (`noindex`, `robots.txt`).
