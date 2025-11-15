import requests
from bs4 import BeautifulSoup
import re
import json
import time
import logging
import inquirer
import os
from urllib.parse import urlparse

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

BASE_URL = "https://www.pokekalos.fr/jeux/mobile/pocket/cartodex/extensions/"
BASE_URL_GameScrapped = "https://ptcgp.raenonx.cc/api/data/global-master"
PROMO_A_URL = "https://www.pokekalos.fr/jeux/mobile/pocket/cartodex/extensions/promo-a/cartes/"

# Version de test avec seulement 10 cartes par set
sets = {
    "puissance-genetique": {"id": "A1", "max_cards": 286, "name": "Genetic Apex"},
    "l-ile-fabuleuse": {"id": "A1a", "max_cards": 86, "name": "Mythical Island"},
    "choc-spatio-temporel": {"id": "A2", "max_cards": 207, "name": "Space-Time Smackdown"},
    "lumiere-triomphale": {"id": "A2a", "max_cards": 96, "name": "Triumphant Light"},
    "rejouissances-rayonnantes": {"id": "A2b", "max_cards": 111, "name": "Shining Revelry"},
    "gardiens-astraux": {"id": "A3", "max_cards": 239, "name": "Celestial Guardians"},
    "crise-interdimensionnelle": {"id": "A3a", "max_cards": 103, "name": "Extradimensional Crisis"},
    "la-clairiere-d-evoli": {"id": "A3b", "max_cards": 107, "name": "Eevee Grove"},
    "sagesse-entre-ciel-et-mer": {"id": "A4", "max_cards": 241, "name": "Wisdom of Sea and Sky"},
    # Nouveaux sets
    "source-secrete": {"id": "A4a", "max_cards": 105, "name": "Secluded Springs"},
    "booster-de-luxe-ex": {"id": "A4b", "max_cards": 379, "name": "Deluxe Pack ex"},
    "mega-ascension": {"id": "B1", "max_cards": 331, "name": "Mega Rising"}
}

# Configuration des cartes Promo-A
promo_a_cards = {
    "promo-a": {"id": "PA", "max_cards": 73, "name": "Promo-A"}  # Ajustez max_cards selon le nombre réel de cartes
}

ingame_CardsInfo = {}

# Variables globales
cardIndex = 0
current_set = None

def set_initial_card_index(set_id):
    global cardIndex
    if set_id == "A1a":
        cardIndex = 286
    elif set_id == "A2":
        cardIndex = 377
    elif set_id == "A2a":
        cardIndex = 589
    elif set_id == "A2b":
        cardIndex = 690
    elif set_id == "A3":
        cardIndex = 806
    elif set_id == "A3a":
        cardIndex = 1050
    elif set_id == "A3b":
        cardIndex = 1158
    elif set_id == "A4":
        cardIndex = 1270
    elif set_id == "A4a":
        # Début après A4 (fin 1510) avec un écart de 6
        cardIndex = 1516
    elif set_id == "A4b":
        # Début après A4a (fin 1620) avec un écart de 6
        cardIndex = 1626
    elif set_id == "B1":
        # Début après A4b (fin 2004) avec un écart de 6
        cardIndex = 2010
    else:
        cardIndex = 0

def getInGameCardInfo():
    global ingame_CardsInfo
    logging.info("Récupération des informations des cartes in-game")
    
    # Requête pour récupérer les données
    response = requests.get(BASE_URL_GameScrapped)

    # Vérifie que la requête a réussi
    if response.status_code == 200:
        data = response.json()
        card_entry_map = data.get("cardEntryMap", {})
        expansion_map = data.get("expansionMap", {})

        # Récupérer la liste des cartes promo
        promo_cards = expansion_map.get("PROMO-A", {}).get("cardsInExpansion", [])
        
        # Créer un mapping des cartes promo en utilisant les données de card_entry_map
        for card_id in promo_cards:
            card_data = card_entry_map.get(card_id, {})
            if card_data:
                collectionNums = card_data.get("collectionNums", [])
                if collectionNums:
                    for collection in collectionNums:
                        expansion = collection.get("expansion", {})
                        if expansion.get("id") == "PROMO-A":
                            num = collection.get("num")
                            if num:
                                ingame_CardsInfo[f"PA_{num}"] = card_id
                                logging.debug(f"ID in-game promo trouvé pour PA_{num}: {card_id}")

        # Traiter les cartes normales
        for card_id, card_data in card_entry_map.items():
            collectionNums = card_data.get("collectionNums", {})
            if collectionNums:
                for collection in collectionNums:
                    expansionName = collection.get("expansion", {}).get("id", "")
                    expansionID = collection.get("num", "")
                    if expansionName and expansionID:
                        ingame_CardsInfo[f"{expansionName}_{expansionID}"] = card_id
                        logging.debug(f"ID in-game trouvé pour {expansionName}_{expansionID}: {card_id}")
    else:
        logging.error(f"Erreur lors de la récupération des données. Code: {response.status_code}")

def extract_id_ingame(set_id, set_details):
    try:
        # Pour les cartes promo, utiliser PROMO-A au lieu de PA
        if set_id == "PA":
            set_id = "PROMO-A"
        ingame_id = ingame_CardsInfo[f"{set_id}_{set_details}"]
        logging.debug(f"ID in-game trouvé pour {set_id}_{set_details}: {ingame_id}")
        return ingame_id
    except Exception as e:
        logging.warning(f"ID in-game non trouvé pour {set_id}_{set_details}")
        return ""

def extract_wp_gp_eligible(set_id, card_number, rarity):
    isShiny = (
        (set_id == "A2b" and int(card_number) >= 97) or
        (set_id == "A3" and int(card_number) >= 210) or
        (set_id == "A3a" and int(card_number) >= 89) or
        (set_id == "A3b" and int(card_number) >= 93) or
        (set_id == "A4" and int(card_number) >= 212) or
        (set_id == "A4a" and int(card_number) >= 91) or
        (set_id == "A4b" and int(card_number) >= 377) or
        (set_id == "B1" and int(card_number) >= 287)
    )
    fitStars = rarity == "☆☆" or rarity == "☆"
    eligible = fitStars and not isShiny
    logging.debug(f"Vérification éligibilité WP/GP - Set: {set_id}, Carte: {card_number}, Shiny: {isShiny}, Stars: {fitStars}, Éligible: {eligible}")
    return eligible

def extract_rarity(soup, is_promo=False):
    if is_promo:
        return ""

    # Trouver la div avec la classe item flexItem
    rarity_div = soup.find('div', class_='item flexItem')
    if not rarity_div:
        logging.warning("Div de rareté non trouvée")
        return ""

    # Chercher d'abord les images avec la classe carte_rarete (diamants et couronnes)
    rarity_imgs = rarity_div.find_all('img', class_='carte_rarete')
    
    # Si pas trouvé, chercher les images avec la classe carte_icone (étoiles)
    if not rarity_imgs:
        rarity_imgs = rarity_div.find_all('img', class_='carte_icone')
        if not rarity_imgs:
            logging.warning("Aucune image de rareté trouvée")
            return ""

    # Vérifier le type de rareté basé sur la première image
    first_img_src = rarity_imgs[0].get('src', '')
    count = len(rarity_imgs)
    logging.debug(f"Nombre d'images de rareté trouvées : {count}, Source première image : {first_img_src}")

    if "diamant" in first_img_src:
        return "◊" * count
    elif "etoile" in first_img_src:
        return "☆" * count
    elif "couronne" in first_img_src:
        return "Crown Rare"
    elif "shiny" in first_img_src:
        return "☆" * count

    logging.warning(f"Type de rareté non reconnu: {first_img_src}")
    return ""

def extract_image(soup, set_id, card_number):
    center_tag = soup.find('center')
    if center_tag:
        img_tag = center_tag.find('img')
        if img_tag and 'src' in img_tag.attrs:
            image_url = img_tag['src']
            logging.debug(f"URL de l'image trouvée: {image_url}")
            return image_url
    logging.warning("Aucune image trouvée dans le HTML")
    return ""

def extract_card_info(soup, set_id, card_number):
    logging.debug(f"Extraction des informations pour la carte {set_id} - {card_number}")
    card_info = {}
    
    card_info["id"] = extract_id()
    logging.debug(f"ID généré: {card_info['id']}")
    
    card_info["id_set"] = str(card_number)
    card_info["name"] = extract_name(soup)
    logging.debug(f"Nom de la carte: {card_info['name']}")
    
    card_info["image"] = extract_image(soup, set_id, card_number)
    logging.debug(f"Chemin de l'image: {card_info['image']}")
    
    is_promo = set_id == "promo-a"
    card_info["rarity"] = extract_rarity(soup, is_promo)
    logging.debug(f"Rareté: {card_info['rarity']}")
    
    card_info["set_details"] = f"{sets[set_id]['name']}  ({sets[set_id]['id']})" if not is_promo else f"{promo_a_cards[set_id]['name']}  ({promo_a_cards[set_id]['id']})"
    card_info["set_subpack"] = extract_set_subpack(soup)
    logging.debug(f"Sous-pack: {card_info['set_subpack']}")
    
    card_info["id_ingame"] = extract_id_ingame(sets[set_id]["id"], card_number) if not is_promo else extract_id_ingame(promo_a_cards[set_id]["id"], card_number)
    
    card_info["wp_gp_eligible"] = extract_wp_gp_eligible(sets[set_id]["id"], card_number, card_info["rarity"]) if not is_promo else False
    logging.debug(f"Éligible WP/GP: {card_info['wp_gp_eligible']}")
    
    return card_info

def extract_id():
    global cardIndex
    currentCardIndex = cardIndex
    cardIndex += 1
    
    # Gestion des sauts d'IDs
    if currentCardIndex == 371:
        cardIndex = 377
        return 371
    elif currentCardIndex > 371 and currentCardIndex < 377:
        return currentCardIndex + 6
    elif currentCardIndex == 583:
        cardIndex = 589
        return 583
    elif currentCardIndex > 583 and currentCardIndex < 589:
        return currentCardIndex + 6
    elif currentCardIndex == 684:
        cardIndex = 690
        return 684
    elif currentCardIndex > 684 and currentCardIndex < 690:
        return currentCardIndex + 6
    elif currentCardIndex == 800:
        cardIndex = 806
        return 800
    elif currentCardIndex > 800 and currentCardIndex < 806:
        return currentCardIndex + 6
    elif currentCardIndex == 1044:
        cardIndex = 1050
        return 1044
    elif currentCardIndex > 1044 and currentCardIndex < 1050:
        return currentCardIndex + 6
    elif currentCardIndex == 1152:
        cardIndex = 1158
        return 1152
    elif currentCardIndex > 1152 and currentCardIndex < 1158:
        return currentCardIndex + 6
    elif currentCardIndex == 1264:
        cardIndex = 1270
        return 1264
    elif currentCardIndex > 1264 and currentCardIndex < 1270:
        return currentCardIndex + 6
    # Fins de sets et sauts suivants
    elif currentCardIndex == 1510:  # fin A4
        cardIndex = 1516
        return 1510
    elif currentCardIndex > 1510 and currentCardIndex < 1516:
        return currentCardIndex + 6
    elif currentCardIndex == 1620:  # fin A4a
        cardIndex = 1626
        return 1620
    elif currentCardIndex > 1620 and currentCardIndex < 1626:
        return currentCardIndex + 6
    elif currentCardIndex == 2004:  # fin A4b
        cardIndex = 2010
        return 2004
    elif currentCardIndex > 2004 and currentCardIndex < 2010:
        return currentCardIndex + 6
    return currentCardIndex

def extract_name(soup):
    title_div = soup.find('h1', class_='title-page')
    if title_div:
        # Diviser le texte par les tirets et prendre le dernier élément
        name = title_div.text.strip().split(' - ')[-1]
        logging.debug(f"Nom trouvé dans le HTML: {name}")
        return name
    logging.warning("Aucun nom trouvé dans le HTML")
    return ""

def extract_set_subpack(soup):
    # Trouver la liste ul avec le style spécifié
    pack_list = soup.find('ul', style='margin-top: .5em;')
    if not pack_list:
        logging.warning("Liste des packs non trouvée")
        return ""

    # Vérifier s'il y a plusieurs items
    pack_items = pack_list.find_all('li')
    if len(pack_items) > 1:
        logging.debug("Plusieurs packs trouvés, utilisation de 'Every'")
        return "Every pack"

    # Récupérer le dernier mot du pack
    pack_link = pack_list.find('a')
    if not pack_link:
        logging.warning("Lien du pack non trouvé")
        return ""

    pack_name = pack_link.text.strip().split()[-1]
    logging.debug(f"Nom du pack trouvé : {pack_name}")

    # Appliquer les règles de remplacement
    # Si des symboles de rareté apparaissent, forcer "Every Pack"
    if ("◊" in pack_name) or ("☆" in pack_name) or ("Crown" in pack_name):
        return "Every Pack"
    if pack_name == "Dracaufeu":
        return "Charizard pack"
    elif pack_name == "Arceus":
        return "Every pack"
    elif pack_name == "Mew":
        return "Every pack"
    elif pack_name == "Rayonnantes":
        return "Every pack"
    elif pack_name == "Interdimensionnelle":
        return "Every pack" 
    elif pack_name == "d'Évoli":
        return "Every pack"
    elif pack_name == "Méga-Braségali":
        return "Mega Blaziken pack"
    elif pack_name == "Méga-Léviator":
        return "Mega Gyarados pack"
    elif pack_name == "Méga-Altaria":
        return "Mega Altaria pack"
    else:
        return f"{pack_name} pack"

def select_sets():
    questions = [
        inquirer.Checkbox('sets',
            message="Sélectionnez les sets à scraper (utilisez les flèches et la barre d'espace pour sélectionner)",
            choices=[(f"{set_info['name']} ({set_info['id']})", set_url) for set_url, set_info in sets.items()]
        ),
    ]
    answers = inquirer.prompt(questions)
    if not answers or not answers['sets']:
        logging.warning("Aucun set sélectionné, arrêt du script")
        exit()
    return answers['sets']

def convert_cards_to_json():
    selected_sets = select_sets()
    cards = []
    eligible_cards = {}
    error_tracker = 0
    total_cards = sum(sets[set_url]["max_cards"] for set_url in selected_sets)
    processed_cards = 0

    logging.info(f"Début du scraping de {total_cards} cartes au total")

    for set_url in selected_sets:
        set_info = sets[set_url]
        logging.info(f"Traitement du set {set_info['name']} ({set_info['id']}) - {set_info['max_cards']} cartes")
        
        # Initialiser l'index de carte pour ce set
        set_initial_card_index(set_info['id'])
        
        for i in range(1, set_info["max_cards"] + 1):
            url = f"{BASE_URL}{set_url}/cartes/{i}.html"
            logging.debug(f"Tentative d'accès à l'URL: {url}")
            
            try:
                response = requests.get(url)
                logging.debug(f"Statut de la réponse: {response.status_code}")
                
                if response.status_code != 200:
                    logging.error(f"Erreur HTTP {response.status_code} pour l'URL: {url}")
                    raise Exception(f"Erreur HTTP {response.status_code}")
                
                soup = BeautifulSoup(response.content, "html.parser")
                card_info = extract_card_info(soup, set_url, i)
                
                processed_cards += 1
                progress = (processed_cards / total_cards) * 100
                logging.info(f"Progression: {progress:.2f}% - Carte {set_url} - {i} traitée")
                
                error_tracker = 0
            except Exception as e:
                logging.error(f"Erreur lors du traitement de la carte {set_url} - {i}: {str(e)}")
                error_tracker += 1
                if error_tracker > 4:
                    logging.warning(f"Trop d'erreurs consécutives, arrêt du set à la carte {i}")
                    break
                continue

            cards.append(card_info)

            if card_info.get("wp_gp_eligible"):
                if set_info["id"] not in eligible_cards:
                    eligible_cards[set_info["id"]] = []
                eligible_cards[set_info["id"]].append(card_info["id_ingame"])
                logging.debug(f"Carte {card_info['id_ingame']} ajoutée aux éligibles")

            time.sleep(1)

    logging.info(f"Sauvegarde des données - {len(cards)} cartes traitées")
    
    # Sauvegarde du fichier principal
    filename = "pokemon_cards_fr.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(cards, file, ensure_ascii=False, indent=4)
    logging.info(f"Fichier principal sauvegardé: {filename}")

    # Sauvegarde du fichier des éligibles
    eligible_filename = "pokemon_cards_fr_wp_eligible.json"
    with open(eligible_filename, "w", encoding="utf-8") as file:
        json.dump(eligible_cards, file, ensure_ascii=False, indent=4)
    logging.info(f"Fichier des éligibles sauvegardé: {eligible_filename}")

def convert_promo_a_cards_to_json():
    cards = []
    error_tracker = 0
    total_cards = promo_a_cards["promo-a"]["max_cards"]
    processed_cards = 0

    logging.info(f"Début du scraping des cartes Promo-A - {total_cards} cartes au total")
    
    for i in range(1, total_cards + 1):
        url = f"{PROMO_A_URL}{i}.html"
        logging.debug(f"Tentative d'accès à l'URL: {url}")
        
        try:
            response = requests.get(url)
            logging.debug(f"Statut de la réponse: {response.status_code}")
            
            if response.status_code != 200:
                logging.error(f"Erreur HTTP {response.status_code} pour l'URL: {url}")
                raise Exception(f"Erreur HTTP {response.status_code}")
            
            soup = BeautifulSoup(response.content, "html.parser")
            card_info = extract_card_info(soup, "promo-a", i)
            
            processed_cards += 1
            progress = (processed_cards / total_cards) * 100
            logging.info(f"Progression: {progress:.2f}% - Carte Promo-A {i} traitée")
            
            error_tracker = 0
        except Exception as e:
            logging.error(f"Erreur lors du traitement de la carte Promo-A {i}: {str(e)}")
            error_tracker += 1
            if error_tracker > 4:
                logging.warning(f"Trop d'erreurs consécutives, arrêt du scraping à la carte {i}")
                break
            continue

        cards.append(card_info)
        time.sleep(1)

    logging.info(f"Sauvegarde des données Promo-A - {len(cards)} cartes traitées")
    
    # Sauvegarde du fichier principal
    filename = "pokemon_cards_promo_a.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(cards, file, ensure_ascii=False, indent=4)
    logging.info(f"Fichier principal Promo-A sauvegardé: {filename}")

# Exécution du script
if __name__ == "__main__":
    logging.info("Démarrage du script de scraping")
    init_time = time.time()
    cardIndex = 0
    getInGameCardInfo()  # Récupération des IDs in-game avant de commencer le scraping
    
    # Demander à l'utilisateur ce qu'il veut scraper
    questions = [
        inquirer.List('scrape_type',
            message="Que souhaitez-vous scraper ?",
            choices=[
                ('Cartes Promo-A uniquement', 'promo'),
                ('Sets normaux uniquement', 'sets'),
                ('Les deux', 'both')
            ]
        ),
    ]
    answers = inquirer.prompt(questions)
    
    if answers:
        if answers['scrape_type'] in ['promo', 'both']:
            convert_promo_a_cards_to_json()
        
        if answers['scrape_type'] in ['sets', 'both']:
            convert_cards_to_json()
    
    end_time = time.time()
    duration = end_time - init_time
    logging.info(f"Téléchargement des cartes terminé. Temps total : {duration:.2f} secondes") 