import os
import json
import sys
import re
import subprocess
from pathlib import Path

# Configuration de l'encodage pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

IMAGES_DIR = "images"
OUTPUT_FILE = "index.html"
GIT_REPO_URL = "https://github.com/LosDaemons13/PTCGP_Images.git"

def get_image_structure():
    """Scanne la structure des images et retourne un dictionnaire organisé par set uniquement"""
    structure = {}
    
    if not os.path.exists(IMAGES_DIR):
        print(f"❌ Le dossier {IMAGES_DIR} n'existe pas!")
        return structure
    
    for set_id in sorted(os.listdir(IMAGES_DIR)):
        set_path = os.path.join(IMAGES_DIR, set_id)
        if not os.path.isdir(set_path):
            continue
        
        images = []
        # Scanner directement dans le dossier du set (pas de sous-dossiers subpack)
        for filename in os.listdir(set_path):
            file_path = os.path.join(set_path, filename)
            # Ignorer les sous-dossiers (anciens subpacks)
            if os.path.isdir(file_path):
                continue
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                images.append(filename)
        
        # Trier les images par ID numérique (extrait depuis le nom du fichier)
        def extract_id_for_sort(filename):
            # Format attendu: A1a_001_EN.webp -> extraire 001
            match = re.search(r'_(\d+)_', filename)
            if match:
                return int(match.group(1))
            return 0  # Par défaut si le format n'est pas reconnu
        
        images.sort(key=extract_id_for_sort)
        
        if images:
            structure[set_id] = images
    
    return structure

def generate_html(structure):
    """Génère un fichier HTML pour naviguer dans les images"""
    html_template = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pokémon TCG Pocket - Images</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-align: center;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .set {{
            margin-bottom: 40px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            background: #f9f9f9;
        }}
        .set-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 1.5em;
            font-weight: bold;
        }}
        .subpack {{
            margin-bottom: 25px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .subpack-title {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .images-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}
        .image-card {{
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 10px;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }}
        .image-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .image-card img {{
            width: 100%;
            height: auto;
            border-radius: 5px;
            display: block;
        }}
        .image-name {{
            margin-top: 8px;
            font-size: 0.85em;
            color: #666;
            text-align: center;
            word-break: break-word;
        }}
        .stats {{
            text-align: center;
            margin-bottom: 30px;
            padding: 15px;
            background: #f0f0f0;
            border-radius: 8px;
        }}
        .stats span {{
            margin: 0 15px;
            font-weight: bold;
            color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎴 Pokémon TCG Pocket - Images</h1>
        <p class="subtitle">Collection complète des images de cartes</p>
        
        <div class="stats">
            <span>📦 Sets: {total_sets}</span>
            <span>🖼️ Images: {total_images}</span>
        </div>
"""
    
    # Calculer les statistiques
    total_sets = len(structure)
    total_images = sum(len(images) for images in structure.values())
    
    html = html_template.format(
        total_sets=total_sets,
        total_images=total_images
    )
    
    # Générer le contenu pour chaque set
    for set_id, images in sorted(structure.items()):
        html += f"""
        <div class="set">
            <div class="set-header">Set: {set_id} ({len(images)} images)</div>
            <div class="images-grid">
"""
        
        for image in images:
            image_path = f"{IMAGES_DIR}/{set_id}/{image}"
            # Nettoyer le nom pour l'affichage
            display_name = image.replace('_', ' ').replace('.webp', '').replace('.png', '').replace('.jpg', '')
            html += f"""
                <div class="image-card" onclick="window.open('{image_path}', '_blank')">
                    <img src="{image_path}" alt="{display_name}" loading="lazy">
                    <div class="image-name">{display_name}</div>
                </div>
"""
        
        html += """
            </div>
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("🎴 Génération de l'index HTML pour GitHub Pages\n")
    
    print("📂 Scan de la structure des images...")
    structure = get_image_structure()
    
    if not structure:
        print("❌ Aucune image trouvée!")
        return
    
    print(f"✅ Structure trouvée:")
    for set_id, images in structure.items():
        print(f"  - {set_id}: {len(images)} image(s)")
    
    print(f"\n📝 Génération du fichier {OUTPUT_FILE}...")
    html_content = generate_html(structure)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Fichier {OUTPUT_FILE} créé avec succès!")
    
    # Push automatique sur GitHub
    print(f"\n🔄 Pushing to GitHub...")
    git_push()
    
    print(f"\n💡 Votre site sera accessible sur: https://losdaemons13.github.io/PTCGP_Images/")
    print(f"   Les images seront accessibles directement via les URLs dans le HTML")

def git_push(repo_path="."):
    """Push automatiquement les changements sur GitHub"""
    try:
        # Vérifier si git est initialisé
        if not os.path.exists(os.path.join(repo_path, ".git")):
            print("\n📦 Initializing Git repository...")
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
                print(f"🔄 Renaming branch '{current_branch}' to 'main'...")
                subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True, capture_output=True)
            else:
                # Créer la branche main si aucune branche n'existe
                subprocess.run(["git", "checkout", "-b", "main"], cwd=repo_path, check=True, capture_output=True)
        
        # Vérifier le remote
        result = subprocess.run(["git", "remote", "get-url", "origin"], 
                              cwd=repo_path, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"🔗 Adding remote origin: {GIT_REPO_URL}")
            subprocess.run(["git", "remote", "add", "origin", GIT_REPO_URL], 
                          cwd=repo_path, check=True, capture_output=True)
        else:
            # Mettre à jour l'URL si nécessaire
            current_url = result.stdout.strip()
            if current_url != GIT_REPO_URL:
                subprocess.run(["git", "remote", "set-url", "origin", GIT_REPO_URL], 
                              cwd=repo_path, check=True, capture_output=True)
        
        # Ajouter tous les fichiers
        print("📝 Adding files to Git...")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        
        # Commit
        print("💾 Committing changes...")
        subprocess.run(["git", "commit", "-m", "Update index.html"], 
                      cwd=repo_path, check=True, capture_output=True)
        
        # Push sur main (forcer)
        print("🚀 Pushing to GitHub (main branch)...")
        subprocess.run(["git", "push", "-u", "origin", "main"], 
                      cwd=repo_path, check=True, capture_output=True)
        
        print("✅ Successfully pushed to GitHub!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git error: {e}")
        print("   You may need to configure Git credentials or push manually.")
        return False
    except Exception as e:
        print(f"⚠️  Error during Git push: {e}")
        return False

if __name__ == "__main__":
    main()

