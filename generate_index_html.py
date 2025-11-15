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
    """Scanne la structure des images et retourne un dictionnaire organisé par set avec FR et EN"""
    structure = {}
    
    if not os.path.exists(IMAGES_DIR):
        print(f"❌ Le dossier {IMAGES_DIR} n'existe pas!")
        return structure
    
    for set_id in sorted(os.listdir(IMAGES_DIR)):
        set_path = os.path.join(IMAGES_DIR, set_id)
        if not os.path.isdir(set_path):
            continue
        
        images_fr = []
        images_en = []
        
        # Scanner les images dans le dossier du set
        for filename in os.listdir(set_path):
            file_path = os.path.join(set_path, filename)
            if os.path.isdir(file_path):
                continue
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                if filename.endswith('_FR.' + filename.split('.')[-1]) or '_FR.' in filename:
                    images_fr.append(filename)
                elif filename.endswith('_EN.' + filename.split('.')[-1]) or '_EN.' in filename:
                    images_en.append(filename)
        
        # Trier les images par ID numérique
        def extract_id_for_sort(filename):
            match = re.search(r'_(\d+)_', filename)
            if match:
                return int(match.group(1))
            return 0
        
        images_fr.sort(key=extract_id_for_sort)
        images_en.sort(key=extract_id_for_sort)
        
        if images_fr or images_en:
            structure[set_id] = {
                "FR": images_fr,
                "EN": images_en
            }
    
    return structure

def generate_html(structure):
    """Génère un fichier HTML avec onglets FR/EN et sets pliables"""
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
            max-width: 1600px;
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
        .tabs {{
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
            gap: 10px;
        }}
        .tab-button {{
            padding: 12px 30px;
            font-size: 1.1em;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            background: #e0e0e0;
            color: #666;
            transition: all 0.3s;
        }}
        .tab-button:hover {{
            background: #d0d0d0;
        }}
        .tab-button.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .set {{
            margin-bottom: 20px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            background: #f9f9f9;
        }}
        .set-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 1.3em;
            font-weight: bold;
            user-select: none;
        }}
        .set-header:hover {{
            opacity: 0.9;
        }}
        .set-header .toggle {{
            font-size: 0.8em;
            margin-left: 15px;
        }}
        .set-content {{
            display: none;
            padding: 20px;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }}
        .set-content.active {{
            display: block;
            max-height: 10000px;
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
        .lang-section {{
            margin-bottom: 25px;
        }}
        .lang-title {{
            font-size: 1.1em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎴 Pokémon TCG Pocket - Images</h1>
        <p class="subtitle">Collection complète des images de cartes (FR + EN)</p>
        
        <div class="stats">
            <span>📦 Sets: {total_sets}</span>
            <span>🇫🇷 Images FR: {total_images_fr}</span>
            <span>🇬🇧 Images EN: {total_images_en}</span>
            <span>🖼️ Total: {total_images}</span>
        </div>
        
        <div class="tabs">
            <button class="tab-button active" onclick="switchTab('FR'); return false;">🇫🇷 Français</button>
            <button class="tab-button" onclick="switchTab('EN'); return false;">🇬🇧 English</button>
        </div>
"""
    
    # Calculer les statistiques
    total_sets = len(structure)
    total_images_fr = sum(len(images["FR"]) for images in structure.values())
    total_images_en = sum(len(images["EN"]) for images in structure.values())
    total_images = total_images_fr + total_images_en
    
    html = html_template.format(
        total_sets=total_sets,
        total_images_fr=total_images_fr,
        total_images_en=total_images_en,
        total_images=total_images
    )
    
    # Générer le contenu pour chaque set
    for set_id, images in sorted(structure.items()):
        total_set_images = len(images["FR"]) + len(images["EN"])
        html += f"""
        <div class="set">
            <div class="set-header" onclick="toggleSet('{set_id}')">
                <span>Set: {set_id} ({total_set_images} images - FR: {len(images['FR'])} | EN: {len(images['EN'])})</span>
                <span class="toggle" id="toggle-{set_id}">▼</span>
            </div>
            <div class="set-content" id="content-{set_id}">
"""
        
        # Section FR
        if images["FR"]:
            html += f"""
                <div class="lang-section lang-section-FR">
                    <div class="lang-title">🇫🇷 Français ({len(images['FR'])} images)</div>
                    <div class="images-grid">
"""
            for image in images["FR"]:
                image_path = f"{IMAGES_DIR}/{set_id}/{image}"
                display_name = image.replace('_', ' ').replace('.webp', '').replace('.png', '').replace('.jpg', '').replace('_FR', '')
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
        
        # Section EN
        if images["EN"]:
            html += f"""
                <div class="lang-section lang-section-EN">
                    <div class="lang-title">🇬🇧 English ({len(images['EN'])} images)</div>
                    <div class="images-grid">
"""
            for image in images["EN"]:
                image_path = f"{IMAGES_DIR}/{set_id}/{image}"
                display_name = image.replace('_', ' ').replace('.webp', '').replace('.png', '').replace('.jpg', '').replace('_EN', '')
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
        </div>
"""
    
    html += """
    </div>
    
    <script>
        let currentTab = 'FR';
        
        function switchTab(lang) {{
            currentTab = lang;
            
            // Mettre à jour les boutons
            document.querySelectorAll('.tab-button').forEach(btn => {{
                btn.classList.remove('active');
                if (btn.textContent.includes('🇫🇷') && lang === 'FR') {{
                    btn.classList.add('active');
                }} else if (btn.textContent.includes('🇬🇧') && lang === 'EN') {{
                    btn.classList.add('active');
                }}
            }});
            
            // Afficher/masquer les sections selon la langue
            document.querySelectorAll('.lang-section').forEach(section => {{
                if (section.classList.contains('lang-section-' + lang)) {{
                    section.style.display = 'block';
                }} else {{
                    section.style.display = 'none';
                }}
            }});
        }}
        
        function toggleSet(setId) {{
            const content = document.getElementById('content-' + setId);
            const toggle = document.getElementById('toggle-' + setId);
            
            if (content.classList.contains('active')) {{
                content.classList.remove('active');
                toggle.textContent = '▼';
            }} else {{
                content.classList.add('active');
                toggle.textContent = '▲';
            }}
        }}
        
        // Initialiser l'affichage
        document.addEventListener('DOMContentLoaded', function() {{
            switchTab('FR');
        }});
    </script>
</body>
</html>
"""
    
    return html

def git_push(repo_path="."):
    """Push automatiquement les changements sur GitHub"""
    try:
        if not os.path.exists(os.path.join(repo_path, ".git")):
            print("\n📦 Initialisation du dépôt Git...")
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True, capture_output=True)
        
        branch_result = subprocess.run(["git", "branch", "--show-current"], 
                                      cwd=repo_path, capture_output=True, text=True)
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else ""
        
        if current_branch != "main":
            if current_branch:
                print(f"🔄 Renommage de la branche '{current_branch}' en 'main'...")
                subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True, capture_output=True)
            else:
                subprocess.run(["git", "checkout", "-b", "main"], cwd=repo_path, check=True, capture_output=True)
        
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
        
        print("📝 Ajout des fichiers à Git...")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        
        print("💾 Commit des changements...")
        subprocess.run(["git", "commit", "-m", "Update index.html"], 
                      cwd=repo_path, check=True, capture_output=True)
        
        print("🚀 Push sur GitHub (branche main)...")
        subprocess.run(["git", "push", "-u", "origin", "main"], 
                      cwd=repo_path, check=True, capture_output=True)
        
        print("✅ Push sur GitHub réussi!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Erreur Git: {e}")
        print("   Vous devrez peut-être configurer les identifiants Git ou push manuellement.")
        return False
    except Exception as e:
        print(f"⚠️  Erreur lors du push Git: {e}")
        return False

def main():
    print("🎴 Génération de l'index HTML pour GitHub Pages\n")
    
    print("📂 Scan de la structure des images...")
    structure = get_image_structure()
    
    if not structure:
        print("❌ Aucune image trouvée!")
        return
    
    print(f"✅ Structure trouvée:")
    for set_id, images in structure.items():
        print(f"  - {set_id}: FR: {len(images['FR'])} | EN: {len(images['EN'])}")
    
    print(f"\n📝 Génération du fichier {OUTPUT_FILE}...")
    html_content = generate_html(structure)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Fichier {OUTPUT_FILE} créé avec succès!")
    
    # Push automatique sur GitHub
    print(f"\n🔄 Push sur GitHub...")
    git_push()
    
    print(f"\n💡 Votre site sera accessible sur: https://losdaemons13.github.io/PTCGP_Images/")
    print(f"   Les images seront accessibles directement via les URLs dans le HTML")

if __name__ == "__main__":
    main()

