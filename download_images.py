import json
import os
import requests
import inquirer
import re
import subprocess
import sys
from urllib.parse import urlparse
from pathlib import Path

# Configuration
IMAGES_DIR = "images"
GIT_REPO_URL = "https://github.com/LosDaemons13/PTCGP_Images.git"
JSON_FR = "PokeScrap fr/pokemon_cards_fr.json"
JSON_EN = "PokeScrap en/pokemon_cards_en.json"

def extract_set_id(set_details):
    """Extrait l'ID du set depuis set_details"""
    match = re.search(r'\(([A-Z0-9a-z]+)\)', set_details)
    if match:
        return match.group(1)
    return None

def get_file_extension(url):
    """Récupère l'extension du fichier depuis l'URL"""
    parsed = urlparse(url)
    path = parsed.path
    if '.' in path:
        return os.path.splitext(path)[1]
    return '.webp'  # Extension par défaut

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

def get_available_sets(cards_fr, cards_en):
    """Récupère la liste des sets disponibles dans les deux fichiers JSON"""
    sets = {}
    
    # Traiter les cartes françaises
    for card in cards_fr:
        set_id = extract_set_id(card.get("set_details", ""))
        if set_id:
            if set_id not in sets:
                sets[set_id] = {
                    "id": set_id,
                    "name": card.get("set_details", "").split("(")[0].strip(),
                    "count_fr": 0,
                    "count_en": 0
                }
            sets[set_id]["count_fr"] += 1
    
    # Traiter les cartes anglaises
    for card in cards_en:
        set_id = extract_set_id(card.get("set_details", ""))
        if set_id:
            if set_id not in sets:
                # Si le set n'existe pas encore, créer l'entrée
                sets[set_id] = {
                    "id": set_id,
                    "name": card.get("set_details", "").split("(")[0].strip(),
                    "count_fr": 0,
                    "count_en": 0
                }
            sets[set_id]["count_en"] += 1
    
    return sets

def select_sets(available_sets):
    """Permet à l'utilisateur de sélectionner les sets à télécharger"""
    choices = [
        ("Tout sélectionner", "ALL")
    ]
    
    # Ajouter chaque set avec son nombre de cartes
    for set_id, set_info in sorted(available_sets.items()):
        display_name = f"{set_info['name']} ({set_id}) - FR: {set_info['count_fr']} | EN: {set_info['count_en']}"
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

def download_images_unified(cards_fr, cards_en, selected_sets):
    """Télécharge les images FR et EN dans le même dossier images"""
    # Organiser les cartes par set et langue
    organized = {}
    
    # Traiter les cartes françaises
    for card in cards_fr:
        set_id = extract_set_id(card.get("set_details", ""))
        if set_id and set_id in selected_sets:
            if set_id not in organized:
                organized[set_id] = {"FR": [], "EN": []}
            organized[set_id]["FR"].append({
                "id_set": card.get("id_set", ""),
                "name": card.get("name", ""),
                "url": card.get("image", "")
            })
    
    # Traiter les cartes anglaises
    for card in cards_en:
        set_id = extract_set_id(card.get("set_details", ""))
        if set_id and set_id in selected_sets:
            if set_id not in organized:
                organized[set_id] = {"FR": [], "EN": []}
            organized[set_id]["EN"].append({
                "id_set": card.get("id_set", ""),
                "name": card.get("name", ""),
                "url": card.get("image", "")
            })
    
    # Trier les cartes par ID dans chaque set et langue
    for set_id in organized:
        organized[set_id]["FR"].sort(key=lambda x: int(x["id_set"]))
        organized[set_id]["EN"].sort(key=lambda x: int(x["id_set"]))
    
    # Télécharger les images
    total_images = sum(len(organized[s]["FR"]) + len(organized[s]["EN"]) for s in organized)
    downloaded = 0
    failed = 0
    
    print(f"\n🚀 Début du téléchargement de {total_images} images...\n")
    
    for set_id in sorted(organized.keys()):
        set_name = next((card.get("set_details", "").split("(")[0].strip() 
                        for card in cards_fr + cards_en 
                        if extract_set_id(card.get("set_details", "")) == set_id), set_id)
        print(f"\n{'='*60}")
        print(f"📁 Set: {set_name} ({set_id})")
        print(f"   FR: {len(organized[set_id]['FR'])} cartes | EN: {len(organized[set_id]['EN'])} cartes")
        print(f"{'='*60}")
        
        # Dossier du set
        set_dir = os.path.join(IMAGES_DIR, set_id)
        
        # Télécharger les images FR
        if organized[set_id]["FR"]:
            print(f"\n  🇫🇷 Téléchargement des images FR...")
            for card_info in organized[set_id]["FR"]:
                card_id = card_info["id_set"]
                card_id_padded = str(card_id).zfill(3)
                extension = get_file_extension(card_info["url"])
                filename = f"{set_id}_{card_id_padded}_FR{extension}"
                filepath = os.path.join(set_dir, filename)
                
                if os.path.exists(filepath):
                    print(f"    ✓ Déjà téléchargée: {filename}")
                    downloaded += 1
                    continue
                
                print(f"    ⬇️  Téléchargement: {filename}")
                if download_image(card_info["url"], filepath):
                    downloaded += 1
                    print(f"    ✅ Téléchargée: {filename}")
                else:
                    failed += 1
                    print(f"    ❌ Échec: {filename}")
        
        # Télécharger les images EN
        if organized[set_id]["EN"]:
            print(f"\n  🇬🇧 Téléchargement des images EN...")
            for card_info in organized[set_id]["EN"]:
                card_id = card_info["id_set"]
                card_id_padded = str(card_id).zfill(3)
                extension = get_file_extension(card_info["url"])
                filename = f"{set_id}_{card_id_padded}_EN{extension}"
                filepath = os.path.join(set_dir, filename)
                
                if os.path.exists(filepath):
                    print(f"    ✓ Already downloaded: {filename}")
                    downloaded += 1
                    continue
                
                print(f"    ⬇️  Downloading: {filename}")
                if download_image(card_info["url"], filepath):
                    downloaded += 1
                    print(f"    ✅ Downloaded: {filename}")
                else:
                    failed += 1
                    print(f"    ❌ Failed: {filename}")
    
    print(f"\n{'='*60}")
    print(f"📊 Résumé du téléchargement:")
    print(f"  ✅ Images téléchargées: {downloaded}")
    print(f"  ❌ Images échouées: {failed}")
    print(f"  📁 Dossier: {IMAGES_DIR}/")
    print(f"{'='*60}\n")
    
    return downloaded > 0

def git_push(repo_path="."):
    """Push automatiquement les changements sur GitHub"""
    try:
        # Vérifier si git est initialisé
        if not os.path.exists(os.path.join(repo_path, ".git")):
            print("\n📦 Initialisation du dépôt Git...")
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True, capture_output=True)
        
        # Vérifier la branche actuelle et forcer main
        branch_result = subprocess.run(["git", "branch", "--show-current"], 
                                      cwd=repo_path, capture_output=True, text=True)
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else ""
        
        if current_branch != "main":
            if current_branch:
                print(f"🔄 Renommage de la branche '{current_branch}' en 'main'...")
                subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True, capture_output=True)
            else:
                subprocess.run(["git", "checkout", "-b", "main"], cwd=repo_path, check=True, capture_output=True)
        
        # Vérifier le remote
        result = subprocess.run(["git", "remote", "get-url", "origin"], 
                              cwd=repo_path, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"🔗 Ajout du remote origin: {GIT_REPO_URL}")
            subprocess.run(["git", "remote", "add", "origin", GIT_REPO_URL], 
                          cwd=repo_path, check=True, capture_output=True)
        else:
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
        
        # Push sur main
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

def main():
    print("🎴 Téléchargement des images Pokémon TCG Pocket (FR + EN)\n")
    
    # Vérifier que les fichiers JSON existent
    if not os.path.exists(JSON_FR):
        print(f"❌ Erreur: Le fichier {JSON_FR} n'existe pas!")
        exit(1)
    
    if not os.path.exists(JSON_EN):
        print(f"❌ Erreur: Le fichier {JSON_EN} n'existe pas!")
        exit(1)
    
    # Charger les données JSON
    print(f"📖 Chargement des fichiers JSON...")
    try:
        with open(JSON_FR, 'r', encoding='utf-8') as f:
            cards_fr = json.load(f)
        with open(JSON_EN, 'r', encoding='utf-8') as f:
            cards_en = json.load(f)
        print(f"✅ {len(cards_fr)} cartes FR et {len(cards_en)} cartes EN chargées\n")
    except Exception as e:
        print(f"❌ Erreur lors du chargement des fichiers JSON: {e}")
        exit(1)
    
    # Récupérer les sets disponibles
    available_sets = get_available_sets(cards_fr, cards_en)
    print(f"📦 {len(available_sets)} set(s) disponible(s):")
    for set_id, set_info in sorted(available_sets.items()):
        print(f"  - {set_info['name']} ({set_id}): FR: {set_info['count_fr']} | EN: {set_info['count_en']}")
    
    # Sélectionner les sets
    print()
    selected_sets = select_sets(available_sets)
    
    print(f"\n✅ {len(selected_sets)} set(s) sélectionné(s): {', '.join(selected_sets)}")
    
    # Télécharger les images
    has_downloads = download_images_unified(cards_fr, cards_en, selected_sets)
    
    print("✨ Téléchargement terminé!\n")
    
    # Générer l'index.html après le téléchargement
    if has_downloads:
        print("📝 Génération de l'index.html...")
        try:
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

if __name__ == "__main__":
    main()

