<<<<<<< HEAD
# PokeScrap - Téléchargement et affichage des images Pokémon TCG Pocket

Ce projet permet de télécharger et organiser les images des cartes Pokémon TCG Pocket en français et en anglais, puis de les afficher sur un site web via GitHub Pages.

## Structure du projet

```
PokeScrap/
├── images/                    # Dossier des images (à la racine)
│   ├── A1/
│   │   ├── A1_001_FR.webp
│   │   ├── A1_001_EN.webp
│   │   ├── A1_002_FR.webp
│   │   └── ...
│   ├── A2/
│   └── ...
├── PokeScrap fr/              # Scripts et données françaises
│   ├── pokemon_cards_fr.json
│   └── ...
├── PokeScrap en/              # Scripts et données anglaises
│   ├── pokemon_cards_en.json
│   └── ...
├── download_images.py         # Script unifié de téléchargement
├── generate_index_html.py     # Génération de l'index HTML
└── index.html                 # Page web générée
```
=======
# PokeScrap - Scraper de cartes Pokémon TCG Pocket (Version Anglaise)

Ce script permet de scraper les cartes Pokémon TCG Pocket depuis le site LimitlessTCG et de générer des fichiers JSON avec les informations des cartes.
>>>>>>> a5bd4c7 (Update images and index)

## Installation

1. Assurez-vous d'avoir Python 3.6+ installé
2. Installez les dépendances :

```bash
<<<<<<< HEAD
pip install requests inquirer pillow
```

**Note** : `pillow` est nécessaire pour convertir les images PNG en WebP.

## Utilisation

### Téléchargement des images

Exécutez le script unifié depuis la racine du projet :

```bash
python download_images.py
```

Le script :
- Charge les données depuis `PokeScrap fr/pokemon_cards_fr.json` et `PokeScrap en/pokemon_cards_en.json`
- Affiche tous les sets disponibles avec le nombre de cartes FR et EN
- Permet de sélectionner les sets à télécharger (ou tout sélectionner)
- Télécharge les images FR et EN dans `images/{SET_ID}/`
- Génère automatiquement `index.html`
- Push automatiquement sur GitHub

### Génération de l'index HTML

Pour régénérer uniquement l'index HTML :

```bash
python generate_index_html.py
```

### Conversion PNG → WebP

Pour convertir toutes les images PNG existantes en WebP :

```bash
python convert_png_to_webp.py
```

**Note** : Le script `download_images.py` convertit automatiquement les PNG en WebP lors du téléchargement.

## Format des fichiers

Les images sont nommées selon le format :
- `{SET_ID}_{ID_PADDED}_{LANG}.webp`
- Exemple : `A1_001_FR.webp`, `A1_001_EN.webp`

**Toutes les images sont automatiquement converties en WebP** pour un format uniforme et une meilleure compression.

## Fonctionnalités du site web

Le fichier `index.html` généré inclut :
- ✅ Onglets pour basculer entre FR et EN
- ✅ Sets pliables/dépliables (cliquez sur l'en-tête du set)
- ✅ Grille d'images responsive
- ✅ Statistiques (nombre de sets, images FR, images EN)
- ✅ Images cliquables pour voir en grand

## Push automatique sur GitHub

Les scripts push automatiquement sur :
- Repository : `https://github.com/LosDaemons13/PTCGP_Images.git`
- Branche : `main`
- Site web : `https://losdaemons13.github.io/PTCGP_Images/`

## Sets disponibles

- A1: Genetic Apex
- A1a: Mythical Island
- A2: Space-Time Smackdown
- A2a: Triumphant Light
- A2b: Shining Revelry
- A3: Celestial Guardians
- A3a: Extradimensional Crisis
- A3b: Eevee Grove
- A4: Wisdom of Sea and Sky
- A4a: Secluded Springs
- A4b: Deluxe Pack ex
- B1: Mega Rising

=======
pip install requests beautifulsoup4 inquirer
```

## Utilisation

### Mode Interactif (Recommandé)

Lancez simplement le script sans arguments pour utiliser le mode interactif :

```bash
python pokemontcgp_scrapper.py
```

Vous pourrez alors sélectionner les sets que vous souhaitez scraper à l'aide d'une interface interactive.

### Arguments en ligne de commande

```bash
# Scraper tous les sets
python pokemontcgp_scrapper.py --all

# Scraper des sets spécifiques
python pokemontcgp_scrapper.py --sets A1 A2 A3

# Mode interactif explicite
python pokemontcgp_scrapper.py --interactive

# Définir une plage d'IDs personnalisée
python pokemontcgp_scrapper.py --start 1 --end 100 --sets A1
```

## Sets disponibles

- **A1**: Genetic Apex (286 cartes)
- **A1a**: Mythical Island (86 cartes)
- **A2**: Space-Time Smackdown (207 cartes)
- **A2a**: Triumphant Light (96 cartes)
- **A2b**: Shining Revelry (111 cartes)
- **A3**: Celestial Guardians (239 cartes)
- **A3a**: Extradimensional Crisis (103 cartes)
- **A3b**: Eevee Grove (107 cartes)
- **A4**: Wisdom of Sea and Sky (241 cartes)

## Fichiers générés

Le script génère deux fichiers :

1. **pokemon_cards_en.json** : Contient toutes les informations des cartes scrappées
2. **pokemon_cards_en_eligible.json** : Contient uniquement les IDs des cartes éligibles pour WP/GP

## Fonctionnalités

- ✅ Sélection interactive des sets
- ✅ Suivi de progression en temps réel
- ✅ Gestion des erreurs avec arrêt automatique après 4 erreurs consécutives
- ✅ Extraction des IDs in-game depuis l'API officielle
- ✅ Détection automatique de l'éligibilité WP/GP
- ✅ Sauvegarde des données au format JSON

## Notes

- Le script inclut un délai de 1 seconde entre chaque requête pour éviter de surcharger le serveur
- Les cartes éligibles WP/GP sont déterminées selon les règles du jeu (étoiles et non-shiny)
- Les IDs in-game sont récupérés depuis l'API officielle de Pokémon TCG Pocket
>>>>>>> a5bd4c7 (Update images and index)
