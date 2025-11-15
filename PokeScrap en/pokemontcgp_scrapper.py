# Based on https://github.com/LucachuTW/CARDS-PokemonPocket-scrapper
# Execute it to update PokemonCards_WPEligible.json & PokemonCards.json
#
# Variables packs & sets needs to be modified

import requests
from bs4 import BeautifulSoup
import re
import json
import time
import argparse
import inquirer

BASE_URL = "https://pocket.limitlesstcg.com/cards/"
BASE_URL_GameScrapped = "https://ptcgp.raenonx.cc/api/data/global-master"

packs = [
	"Pikachu pack",
	"Charizard pack",
	"Mewtwo pack",
	"Dialga pack",
	"Palkia pack",
	"Solgaleo pack",
	"Luanala pack",
	"Ho-Oh pack",
	"Lugia pack",
	# Nouveaux boosters B1
	"Mega Blaziken pack",
	"Mega Gyarados pack",
	"Mega Altaria pack",
]

# Définition des sets avec leurs informations
sets_info = {
	"A1": {"name": "Genetic Apex", "max_cards": 286},
	"A1a": {"name": "Mythical Island", "max_cards": 86},
	"A2": {"name": "Space-Time Smackdown", "max_cards": 207},
	"A2a": {"name": "Triumphant Light", "max_cards": 96},
	"A2b": {"name": "Shining Revelry", "max_cards": 111},
	"A3": {"name": "Celestial Guardians", "max_cards": 239},
	"A3a": {"name": "Extradimensional Crisis", "max_cards": 103},
	"A3b": {"name": "Eevee Grove", "max_cards": 107},
	"A4": {"name": "Wisdom of Sea and Sky", "max_cards": 241},
	# Nouveaux sets
	"A4a": {"name": "Secluded Springs", "max_cards": 105},
	"A4b": {"name": "Deluxe Pack ex", "max_cards": 379},
	"B1": {"name": "Mega Rising", "max_cards": 331},
}

sets = list(sets_info.keys())

# Map nom d'affichage -> code set (normalise ": " en " ")
name_to_code = { info["name"]: code for code, info in sets_info.items() }

def prompt_cards_limit():
	"""Demande à l'utilisateur combien de cartes extraire par set (vide = tout)."""
	questions = [
		inquirer.Text(
			'count',
			message="Combien de cartes par set à extraire ? (laisser vide pour tout)",
			default=""
		)
	]
	answers = inquirer.prompt(questions)
	if not answers:
		return None
	value = (answers.get('count') or "").strip()
	if value == "":
		return None
	try:
		count = int(value)
		return count if count > 0 else None
	except:
		print("Entrée invalide, extraction complète par défaut.")
		return None

def set_initial_card_index(set_id):
	"""Définit l'index de carte initial pour chaque set"""
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
		cardIndex = 1516
	elif set_id == "A4b":
		cardIndex = 1626
	elif set_id == "B1":
		cardIndex = 2010
	else:
		cardIndex = 0

def select_sets_interactive():
	"""Fonction pour sélectionner les sets de manière interactive"""
	questions = [
		inquirer.Checkbox('sets',
			message="Sélectionnez les sets à scraper (utilisez les flèches et la barre d'espace pour sélectionner)",
			choices=[(f"{sets_info[set_id]['name']} ({set_id})", set_id) for set_id in sets_info.keys()]
		),
	]
	answers = inquirer.prompt(questions)
	if not answers or not answers['sets']:
		print("❌ Aucun set sélectionné, arrêt du script")
		exit()
	return answers['sets']

def parse_arguments():
	parser = argparse.ArgumentParser(description='Scraper de cartes Pokémon TCG Pocket')
	parser.add_argument('--sets', nargs='+', help='Liste des sets à scraper (ex: A1 A2 A3)')
	parser.add_argument('--all', action='store_true', help='Scraper tous les sets disponibles')
	parser.add_argument('--interactive', action='store_true', help='Mode interactif pour sélectionner les sets')
	parser.add_argument('--start', type=int, default=1, help='ID de début pour le scraping (défaut: 1)')
	parser.add_argument('--end', type=int, default=10000, help='ID de fin pour le scraping (défaut: max du set)')
	return parser.parse_args()

def debug_tag_info(soup, tag_name, class_name=None):
	element = soup.find(tag_name, class_=class_name) if class_name else soup.find(tag_name)
	if element:
		print(f"\n🔍 Balise trouvée: <{tag_name}>")
		if class_name:
			print(f"   Classe: {class_name}")
		# Ne pas afficher le contenu de la table des versions pour éviter "Contenu: Versions"
		if not (tag_name == "table" and class_name == "card-prints-versions"):
			print(f"   Contenu: {element.text.strip()}")
		return element
	else:
		print(f"\n❌ Balise non trouvée: <{tag_name}>")
		if class_name:
			print(f"   Classe recherchée: {class_name}")
		return None

def extract_card_info(soup):
	print("\n📋 Extraction des informations de la carte:")
	print("=" * 50)
	
	card_info = {}
	
	# ID
	card_info["id"] = extract_id(soup)
	print(f"\n🆔 ID de la carte: {card_info['id']}")
	
	# ID Set
	title = debug_tag_info(soup, "p", "card-text-title")
	if title:
		card_info["id_set"] = title.find("a")["href"].split("/")[-1]
		print(f"   ID Set extrait: {card_info['id_set']}")
	
	# Nom
	if title:
		card_info["name"] = title.find("a").text.strip()
		print(f"   Nom extrait: {card_info['name']}")
	
	# Image
	image_div = debug_tag_info(soup, "div", "card-image")
	if image_div:
		card_info["image"] = image_div.find("img")["src"]
		print(f"   URL de l'image extraite: {card_info['image']}")
	
	# Rareté
	rarity_section = debug_tag_info(soup, "table", "card-prints-versions")
	if rarity_section:
		current_version = rarity_section.find("tr", class_="current")
		if current_version:
			card_info["rarity"] = current_version.find_all("td")[-1].text.strip()
			print(f"   Rareté extraite: {card_info['rarity']}")
	
	# Détails du set
	set_info = debug_tag_info(soup, "div", "card-prints-current")
	if set_info:
		set_details = set_info.find("span", class_="text-lg")
		if set_details:
			card_info["set_details"] = set_details.text.strip()
			print(f"   Détails du set extraits: {card_info['set_details']}")
		
		set_number = set_info.find("span").next_sibling
		pack_temp = set_info.find_all("span")[-1].text.strip()
		card_info["set_subpack"] = " ".join(pack_temp.split("·")[-1].split())
		# Normalisation: si des symboles de rareté sont présents, forcer "Every Pack"
		if (
			"◊" in card_info["set_subpack"] or
			"☆" in card_info["set_subpack"] or
			"Crown Rare" in card_info["set_subpack"]
		):
			card_info["set_subpack"] = "Every Pack"
		print(f"   Sous-pack extrait: {card_info['set_subpack']}")
	
	# ID In-game
	card_info["id_ingame"] = extract_id_ingame(card_info["id_set"], card_info["set_details"])
	print(f"   ID In-game extrait: {card_info['id_ingame']}")
	
	# Éligibilité WP/GP
	card_info["wp_gp_eligible"] = extract_wp_gp_eligible(card_info["id_set"], card_info["set_details"], card_info["rarity"])
	print(f"   Éligibilité WP/GP: {card_info['wp_gp_eligible']}")
	
	print("=" * 50)
	return card_info

def extract_id(soup):
	global cardIndex
	currentCardIndex = cardIndex
	cardIndex += 1
	# Gestion des sauts d'IDs pour garder la continuité globale
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

def extract_id_set(soup):
	title = soup.find("p", class_="card-text-title")
	return title.find("a")["href"].split("/")[-1]

def extract_name(soup):
	title = soup.find("p", class_="card-text-title")
	return title.find("a").text.strip()

def extract_id_ingame(id_set, set_details):
	global cardIndex

	start_index = set_details.find('(') + 1
	end_index = set_details.find(')')
	extracted_set = set_details[start_index:end_index] if start_index > 0 and end_index > start_index else ""
	# Si pas de code entre parenthèses, tenter via nom → code
	if not extracted_set:
		normalized_name = set_details.replace(": ", " ").strip()
		extracted_set = name_to_code.get(normalized_name, "")
		if normalized_name == "Deluxe Pack ex":
			print(f"[A4b][extract_id_ingame:name_map] normalized='{normalized_name}', mapped_code='{extracted_set}'")
	# Logs détaillés pour A4b
	if extracted_set == "A4b":
		key = f"{extracted_set}_{id_set}"
		print(f"[A4b][extract_id_ingame] set_details='{set_details}', extracted_set='{extracted_set}', id_set='{id_set}', key='{key}'")
		print(f"[A4b][extract_id_ingame] key in ingame_CardsInfo? {key in ingame_CardsInfo}")

	try:
		ingame_id = ingame_CardsInfo[extracted_set+"_"+id_set]
		if extracted_set == "A4b":
			print(f"[A4b][extract_id_ingame] FOUND ingame_id='{ingame_id}' for key '{extracted_set+'_'+id_set}'")
		return ingame_id
	except Exception as e:
		if extracted_set == "A4b":
			print(f"[A4b][extract_id_ingame] MISSING ingame_id for key '{extracted_set+'_'+id_set}' - error: {e}")
		else:
			print(f"Card {cardIndex} ingame ID not found")
		return ""

def extract_wp_gp_eligible(id_set, set_details, rarity):
	global trainer_cardIndex, pokemon_cardIndex

	isShiny = (
		"(A2b)" in set_details and int(id_set) >= 97 or
		"(A3)" in set_details and int(id_set) >= 210 or
		"(A3a)" in set_details and int(id_set) >= 89 or
		"(A3b)" in set_details and int(id_set) >= 93 or
		"(A4)" in set_details and int(id_set) >= 212 or
		"(A4a)" in set_details and int(id_set) >= 91 or
		"(A4b)" in set_details and int(id_set) >= 377 or
		"(B1)" in set_details and int(id_set) >= 287
	)
	fitStars = rarity == "☆☆" or rarity == "☆"

	return fitStars and not isShiny

def extract_image(soup):
	return soup.find("div", class_="card-image").find("img")["src"]

def extract_rarity_and_fullart(soup):
	rarity_section = soup.find("table", class_="card-prints-versions")
	if rarity_section:
		current_version = rarity_section.find("tr", class_="current")
		rarity = (
			current_version.find_all("td")[-1].text.strip()
			if current_version
			else "Unknown"
		)
	else:
		rarity = "Unknown"
	return rarity

def extract_set_and_pack_info(soup):
	set_info = soup.find("div", class_="card-prints-current")
	if set_info:
		set_details = set_info.find("span", class_="text-lg")
		set_number = set_info.find("span").next_sibling
		set_details = set_details.text.strip() if set_details else "Unknown"
		pack_temp = set_info.find_all("span")[-1].text.strip()
		pack_info = " ".join(pack_temp.split("·")[-1].split())
	# Normalisation complémentaire
	if ("◊" in pack_info) or ("☆" in pack_info) or ("Crown Rare" in pack_info):
		return set_details, "Every Pack"
	return set_details, pack_info if pack_info in packs else "Every pack"
	return "Unknown", "Unknown"

def iterate_all_sets():
	for set_name in sets:
		iterate_per_set(set_name, 96, 285)

def iterate_per_set(set_name, start_id, end_id):
	for i in range(start_id, end_id + 1):
		url = f"{BASE_URL}{set_name}/{i}"
		response = requests.get(url)
		soup = BeautifulSoup(response.content, "html.parser")
		# try:
		card_info = extract_card_info(soup)
		# except Exception as e:
		#     print(f"Error processing card {i}: {e}")
		#     continue

		for key, value in card_info.items():
			print(f"{key}: {value}")
		print("-" * 40)

def convert_cards_to_json(start_id, end_id, selected_sets=None, limit_per_set=None):
	if selected_sets is None:
		selected_sets = sets
	
	print(f"\n🎯 Sets sélectionnés pour le scraping: {', '.join(selected_sets)}")
	print(f"📊 Plage d'IDs: {start_id} à {end_id}")
	
	cards = []
	eligible_cards = {}
	error_tracker = 0
	total_cards = sum(sets_info[set_id]["max_cards"] for set_id in selected_sets)
	processed_cards = 0

	print(f"\n📈 Total de cartes à traiter: {total_cards}")

	for set_name in selected_sets:
		set_info = sets_info[set_name]
		max_cards = set_info["max_cards"]
		
		# Initialiser l'index de carte pour ce set
		set_initial_card_index(set_name)
		
		print(f"\n{'='*50}")
		print(f"Traitement du set: {set_info['name']} ({set_name})")
		print(f"Nombre de cartes dans ce set: {max_cards}")
		print(f"Index de carte initial: {cardIndex}")
		print(f"{'='*50}\n")
		
		# Calcule une borne locale selon la limite demandée et le max du set
		local_end = min(end_id, max_cards)
		if limit_per_set is not None:
			local_end = min(start_id + limit_per_set - 1, max_cards)
		print(f"[Range] {set_name}: {start_id} -> {local_end} (max={max_cards})")
		for i in range(start_id, local_end + 1):
			url = f"{BASE_URL}{set_name}/{i}"
			if set_name == "A4b":
				print(f"[A4b][loop] URL: {url}")
			response = requests.get(url)
			soup = BeautifulSoup(response.content, "html.parser")
			try:
				card_info = extract_card_info(soup)
				if set_name == "A4b":
					# Tentative de clé calculée pour logs
					set_details = card_info.get("set_details", "")
					start_index = set_details.find('(') + 1
					end_index = set_details.find(')')
					extracted_set = set_details[start_index:end_index]
					key = f"{extracted_set}_{card_info.get('id_set')}"
					print(f"[A4b][after_extract] id_set='{card_info.get('id_set')}', set_details='{set_details}', key='{key}', id_ingame='{card_info.get('id_ingame')}'")
				processed_cards += 1
				progress = (processed_cards / total_cards) * 100
				print(f"\n📊 Progression: {progress:.1f}% - Carte {set_name} - {i}")
				print("-" * 30)
				for key, value in card_info.items():
					print(f"{key}: {value}")
				print("-" * 30)
				error_tracker = 0
			except Exception as e:
				print(f"\n❌ Erreur lors du traitement de la carte {set_name} - {i}: {e}")
				error_tracker += 1
				if error_tracker > 4:
					print(f"\n⚠️ Arrêt du traitement après {error_tracker} erreurs consécutives")
					break
				continue

			cards.append(card_info)

			if card_info.get("wp_gp_eligible"):
				if set_name not in eligible_cards:
					eligible_cards[set_name] = []
					
				eligible_cards[set_name].append(card_info["id_ingame"])
				print(f"✅ Carte éligible WP/GP ajoutée: {card_info['name']}")

	# Sauvegarde du fichier principal
	filename = "pokemon_cards_en.json"
	with open(filename, "w", encoding="utf-8") as file:
		json.dump(cards, file, ensure_ascii=False, indent=4)
	print(f"\n💾 Fichier principal sauvegardé: {filename}")

	# Sauvegarde du fichier des éligibles
	eligible_filename = "pokemon_cards_en_eligible.json"
	with open(eligible_filename, "w", encoding="utf-8") as file:
		json.dump(eligible_cards, file, ensure_ascii=False, indent=4)
	print(f"💾 Fichier des cartes éligibles sauvegardé: {eligible_filename}")

def getInGameCardInfo():
	global ingame_CardsInfo
	# Requête pour récupérer les données
	response = requests.get(BASE_URL_GameScrapped)

	# Vérifie que la requête a réussi
	if response.status_code == 200:
		data = response.json()
		
		card_entry_map = data.get("cardEntryMap", {})

		for card_id, card_data in card_entry_map.items():

			# Itérer toutes les entrées pour mapper chaque extension
			collections = card_data.get("collectionNums", [])
			if not isinstance(collections, list):
				collections = [collections]
			for c in collections:
				expansion = c.get("expansion", {}) or {}
				expansionName = expansion.get("id", "")
				expansionID = c.get("num", "")
				if expansionName and expansionID != "":
					ingame_CardsInfo[f"{expansionName}_{expansionID}"] = card_id

		# Logs ciblés A4b
		a4b_keys = [k for k in ingame_CardsInfo.keys() if k.startswith("A4b_")]
		print(f"[A4b][getInGameCardInfo] total keys with prefix 'A4b_': {len(a4b_keys)}")
		print(f"[A4b][getInGameCardInfo] sample keys: {a4b_keys[:10]}")
	else:
		print(f"Erreur lors de la récupération des données. Code: {response.status_code}")

if __name__ == "__main__":
	args = parse_arguments()
	
	if args.interactive:
		selected_sets = select_sets_interactive()
	elif args.all:
		selected_sets = sets
	elif args.sets:
		selected_sets = [s for s in args.sets if s in sets]
		if not selected_sets:
			print("❌ Aucun set valide spécifié. Sets disponibles:", ", ".join(sets))
			print("Sets disponibles avec leurs noms:")
			for set_id, info in sets_info.items():
				print(f"  {set_id}: {info['name']} ({info['max_cards']} cartes)")
			exit(1)
	else:
		print("ℹ️  Aucun set spécifié. Utilisation du mode interactif par défaut.")
		selected_sets = select_sets_interactive()

	print(f"\n🎯 Sets sélectionnés pour le scraping:")
	for set_id in selected_sets:
		info = sets_info[set_id]
		print(f"  - {info['name']} ({set_id}): {info['max_cards']} cartes")

	init_time = time.time()
	cardIndex = 0
	ingame_CardsInfo = {}
	getInGameCardInfo()

	# Demande interactive d'une limite de cartes si on est en mode interactif ou défaut
	limit_per_set = None
	try:
		limit_per_set = prompt_cards_limit()
	except Exception as e:
		print(f"(info) Limite non définie: {e}")

	convert_cards_to_json(args.start, args.end, selected_sets, limit_per_set)

	end_time = time.time()
	print(f"\n⏱️  Temps total d'exécution: {end_time - init_time:.2f} secondes")
