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

## Installation

1. Assurez-vous d'avoir Python 3.6+ installé
2. Installez les dépendances :

```bash
pip install requests inquirer
```

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

## Format des fichiers

Les images sont nommées selon le format :
- `{SET_ID}_{ID_PADDED}_{LANG}.{extension}`
- Exemple : `A1_001_FR.webp`, `A1_001_EN.webp`

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

