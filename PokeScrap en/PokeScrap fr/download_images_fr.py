import json
import os
import requests
import inquirer
import re
import subprocess
import sys
from urllib.parse import urlparse
from pathlib import Path

# Fichier JSON contenant les données des cartes
JSON_FILE = "pokemon_cards_fr.json"
IMAGES_DIR = "images"
GIT_REPO_URL = "https://github.com/LosDaemons13/PTCGP_Images.git"
LANGUAGE = "FR"

def extract_set_id(set_details):
    """Extrait l'ID du set depuis set_details (ex: "Eevee Grove  (A3b)" -> "A3b", "Deluxe Pack ex  (A4b)" -> "A4b")"""
    match = re.search(r'\(([A-Z0-9a-z]+)\)', set_details)
    if match:
        return match.group(1)
    return None

def sanitize_filename(name):
    """Nettoie le nom de fichier pour qu'il soit valide sur tous les systèmes"""
    # Remplacer les caractères invalides
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remplacer les espaces multiples par un seul
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

def get_available_sets(cards):
    """Récupère la liste des sets disponibles dans les données"""
    sets = {}
    for card in cards:
        set_id = extract_set_id(card.get("set_details", ""))
        if set_id:
            if set_id not in sets:
                sets[set_id] = {
                    "id": set_id,
                    "name": card.get("set_details", "").split("(")[0].strip(),
                    "count": 0
                }
            sets[set_id]["count"] += 1
    return sets

def select_sets(available_sets):
    """Permet à l'utilisateur de sélectionner les sets à télécharger"""
    choices = [
        ("Tout sélectionner", "ALL")
    ]
    
    # Ajouter chaque set avec son nombre de cartes
    for set_id, set_info in sorted(available_sets.items()):
        display_name = f"{set_info['name']} ({set_id}) - {set_info['count']} cartes"
        choices.append((display_name, set_id))
    
    questions = [
        inquirer.Checkbox(
            'sets',
            message="Sélectionnez les sets à télécharger (utilisez les flèches et la barre d'espace pour sélectionner)",
            choices=choices
        ),
    ]
    answers = inquirer.prompt(questions)
    
    if not answers or not answers['sets']:
        print("❌ Aucun set sélectionné, arrêt du script")
        exit()
    
    # Si "ALL" est sélectionné, retourner tous les sets
    if "ALL" in answers['sets']:
        return list(available_sets.keys())
    
    return answers['sets']

def download_image(url, filepath, max_retries=3):
    """Télécharge une image avec gestion des erreurs et retries"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Créer le dossier si nécessaire
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Sauvegarder l'image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  ⚠️  Tentative {attempt + 1}/{max_retries} échouée, nouvelle tentative...")
                continue
            else:
                print(f"  ❌ Erreur après {max_retries} tentatives: {e}")
                return False
    return False

def get_file_extension(url):
    """Récupère l'extension du fichier depuis l'URL"""
    parsed = urlparse(url)
    path = parsed.path
    if '.' in path:
        return os.path.splitext(path)[1]
    return '.png'  # Extension par défaut

def download_images_by_set(cards, selected_sets):
    """Télécharge les images organisées uniquement par set"""
    # Filtrer les cartes selon les sets sélectionnés
    filtered_cards = []
    for card in cards:
        set_id = extract_set_id(card.get("set_details", ""))
        if set_id and set_id in selected_sets:
            filtered_cards.append(card)
    
    print(f"\n📦 {len(filtered_cards)} cartes à télécharger pour {len(selected_sets)} set(s)")
    
    # Organiser les cartes par set uniquement
    organized = {}
    for card in filtered_cards:
        set_id = extract_set_id(card.get("set_details", ""))
        image_url = card.get("image", "")
        
        if not set_id or not image_url:
            continue
        
        if set_id not in organized:
            organized[set_id] = []
        
        organized[set_id].append({
            "id_set": card.get("id_set", ""),
            "name": card.get("name", ""),
            "url": image_url
        })
    
    # Trier les cartes par ID dans chaque set
    for set_id in organized:
        organized[set_id].sort(key=lambda x: int(x["id_set"]))
    
    # Télécharger les images
    total_images = sum(len(cards) for cards in organized.values())
    downloaded = 0
    failed = 0
    
    print(f"\n🚀 Début du téléchargement de {total_images} images...\n")
    
    for set_id, cards_list in sorted(organized.items()):
        set_name = next((card.get("set_details", "").split("(")[0].strip() for card in cards if extract_set_id(card.get("set_details", "")) == set_id), set_id)
        print(f"\n{'='*60}")
        print(f"📁 Set: {set_name} ({set_id}) - {len(cards_list)} cartes")
        print(f"{'='*60}")
        
        # Dossier directement dans le set (pas de sous-dossier subpack)
        set_dir = os.path.join(IMAGES_DIR, set_id)
        
        for card_info in cards_list:
            # Déterminer le nom du fichier au format: A1a_001_FR.webp
            card_id = card_info["id_set"]
            # Padding à 3 chiffres
            card_id_padded = str(card_id).zfill(3)
            extension = get_file_extension(card_info["url"])
            filename = f"{set_id}_{card_id_padded}_{LANGUAGE}{extension}"
            filepath = os.path.join(set_dir, filename)
            
            # Vérifier si l'image existe déjà
            if os.path.exists(filepath):
                print(f"    ✓ Déjà téléchargée: {filename}")
                downloaded += 1
                continue
            
            # Télécharger l'image
            print(f"    ⬇️  Téléchargement: {filename}")
            if download_image(card_info["url"], filepath):
                downloaded += 1
                print(f"    ✅ Téléchargée: {filename}")
            else:
                failed += 1
                print(f"    ❌ Échec: {filename}")
    
    print(f"\n{'='*60}")
    print(f"📊 Résumé du téléchargement:")
    print(f"  ✅ Images téléchargées: {downloaded}")
    print(f"  ❌ Images échouées: {failed}")
    print(f"  📁 Dossier: {IMAGES_DIR}/")
    print(f"{'='*60}\n")
    
    return downloaded > 0  # Retourne True si au moins une image a été téléchargée

def main():
    print("🎴 Téléchargement des images Pokémon TCG Pocket (FR)\n")
    
    # Vérifier que le fichier JSON existe
    if not os.path.exists(JSON_FILE):
        print(f"❌ Erreur: Le fichier {JSON_FILE} n'existe pas!")
        print(f"   Assurez-vous d'exécuter le script depuis le dossier 'PokeScrap fr'")
        exit(1)
    
    # Charger les données JSON
    print(f"📖 Chargement du fichier {JSON_FILE}...")
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            cards = json.load(f)
        print(f"✅ {len(cards)} cartes chargées\n")
    except Exception as e:
        print(f"❌ Erreur lors du chargement du fichier JSON: {e}")
        exit(1)
    
    # Récupérer les sets disponibles
    available_sets = get_available_sets(cards)
    print(f"📦 {len(available_sets)} set(s) disponible(s):")
    for set_id, set_info in sorted(available_sets.items()):
        print(f"  - {set_info['name']} ({set_id}): {set_info['count']} cartes")
    
    # Sélectionner les sets
    print()
    selected_sets = select_sets(available_sets)
    
    print(f"\n✅ {len(selected_sets)} set(s) sélectionné(s): {', '.join(selected_sets)}")
    
    # Télécharger les images
    has_downloads = download_images_by_set(cards, selected_sets)
    
    print("✨ Téléchargement terminé!\n")
    
    # Générer l'index.html après le téléchargement
    if has_downloads:
        print("📝 Génération de l'index.html...")
        try:
            # Importer et exécuter la génération de l'index
            from generate_index_html import get_image_structure, generate_html
            structure = get_image_structure()
            if structure:
                html_content = generate_html(structure)
                with open("index.html", 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print("✅ index.html généré avec succès!")
        except Exception as e:
            print(f"⚠️  Erreur lors de la génération de l'index.html: {e}")
    
    # Push automatique sur GitHub
    if has_downloads:
        print("\n🔄 Push sur GitHub...")
        git_push()

def git_push(repo_path="."):
    """Push automatiquement les changements sur GitHub"""
    try:
        # Vérifier si git est initialisé
        if not os.path.exists(os.path.join(repo_path, ".git")):
            print("\n📦 Initialisation du dépôt Git...")
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            # Créer la branche main directement
            subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True, capture_output=True)
        
        # Vérifier la branche actuelle et forcer main
        branch_result = subprocess.run(["git", "branch", "--show-current"], 
                                      cwd=repo_path, capture_output=True, text=True)
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else ""
        
        if current_branch != "main":
            # Renommer la branche en main si elle existe
            if current_branch:
                print(f"🔄 Renommage de la branche '{current_branch}' en 'main'...")
                subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True, capture_output=True)
            else:
                # Créer la branche main si aucune branche n'existe
                subprocess.run(["git", "checkout", "-b", "main"], cwd=repo_path, check=True, capture_output=True)
        
        # Vérifier le remote
        result = subprocess.run(["git", "remote", "get-url", "origin"], 
                              cwd=repo_path, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"🔗 Ajout du remote origin: {GIT_REPO_URL}")
            subprocess.run(["git", "remote", "add", "origin", GIT_REPO_URL], 
                          cwd=repo_path, check=True, capture_output=True)
        else:
            # Mettre à jour l'URL si nécessaire
            current_url = result.stdout.strip()
            if current_url != GIT_REPO_URL:
                subprocess.run(["git", "remote", "set-url", "origin", GIT_REPO_URL], 
                              cwd=repo_path, check=True, capture_output=True)
        
        # Ajouter tous les fichiers
        print("📝 Ajout des fichiers à Git...")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        
        # Commit
        print("💾 Commit des changements...")
        subprocess.run(["git", "commit", "-m", "Update images and index"], 
                      cwd=repo_path, check=True, capture_output=True)
        
        # Push sur main (forcer)
        print("🚀 Push sur GitHub (branche main)...")
        subprocess.run(["git", "push", "-u", "origin", "main"], 
                      cwd=repo_path, check=True, capture_output=True)
        
        print("✅ Push sur GitHub réussi!\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Erreur Git: {e}")
        print("   Vous devrez peut-être configurer les identifiants Git ou push manuellement.")
        return False
    except Exception as e:
        print(f"⚠️  Erreur lors du push Git: {e}")
        return False

if __name__ == "__main__":
    main()

