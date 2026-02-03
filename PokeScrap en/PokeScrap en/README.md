# PokeScrap - Scraper de cartes Pokémon TCG Pocket (Version Anglaise)

Ce script permet de scraper les cartes Pokémon TCG Pocket depuis le site LimitlessTCG et de générer des fichiers JSON avec les informations des cartes.

## Installation

1. Assurez-vous d'avoir Python 3.6+ installé
2. Installez les dépendances :

```bash
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
