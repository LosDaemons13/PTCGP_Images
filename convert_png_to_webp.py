import os
import sys
import argparse
from pathlib import Path
from PIL import Image

# Configuration de l'encodage pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

IMAGES_DIR = "images"

def convert_png_to_webp(filepath):
    """Convertit un fichier PNG en WebP"""
    try:
        # Ouvrir l'image PNG
        img = Image.open(filepath)
        
        # Convertir en RGB si nécessaire (pour les PNG avec transparence)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Créer un fond blanc pour les images avec transparence
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Créer le nom du fichier WebP
        webp_path = os.path.splitext(filepath)[0] + '.webp'
        
        # Sauvegarder en WebP avec une qualité élevée
        img.save(webp_path, 'WEBP', quality=95)
        
        return webp_path
    except Exception as e:
        print(f"    ❌ Erreur lors de la conversion: {e}")
        return None

def scan_and_convert():
    """Scanne le dossier images et convertit tous les PNG en WebP"""
    if not os.path.exists(IMAGES_DIR):
        print(f"❌ Le dossier {IMAGES_DIR} n'existe pas!")
        return
    
    png_files = []
    
    print(f"📂 Scan du dossier {IMAGES_DIR}...")
    
    # Trouver tous les fichiers PNG
    for root, dirs, files in os.walk(IMAGES_DIR):
        for file in files:
            if file.lower().endswith('.png'):
                filepath = os.path.join(root, file)
                png_files.append(filepath)
    
    if not png_files:
        print("✅ Aucun fichier PNG trouvé!")
        return
    
    print(f"📦 {len(png_files)} fichier(s) PNG trouvé(s)\n")
    
    converted = 0
    failed = 0
    deleted = 0
    
    print(f"🔄 Début de la conversion...\n")
    
    for i, png_file in enumerate(png_files, 1):
        relative_path = os.path.relpath(png_file, IMAGES_DIR)
        print(f"[{i}/{len(png_files)}] Conversion: {relative_path}")
        
        # Vérifier si le WebP existe déjà
        webp_path = os.path.splitext(png_file)[0] + '.webp'
        if os.path.exists(webp_path):
            print(f"    ℹ️  WebP existe déjà, suppression du PNG: {os.path.basename(png_file)}")
            try:
                os.remove(png_file)
                deleted += 1
                converted += 1
                continue
            except Exception as e:
                print(f"    ⚠️  Erreur lors de la suppression: {e}")
                failed += 1
                continue
        
        # Convertir en WebP
        webp_path = convert_png_to_webp(png_file)
        
        if webp_path:
            # Vérifier que le fichier WebP existe
            if os.path.exists(webp_path):
                # Supprimer le fichier PNG original
                try:
                    os.remove(png_file)
                    deleted += 1
                    converted += 1
                    print(f"    ✅ Converti et supprimé: {os.path.basename(png_file)}")
                except Exception as e:
                    print(f"    ⚠️  WebP créé mais PNG non supprimé: {e}")
                    converted += 1
            else:
                print(f"    ❌ Le fichier WebP n'a pas été créé")
                failed += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Résumé de la conversion:")
    print(f"  ✅ Images converties: {converted}")
    print(f"  🗑️  Fichiers PNG supprimés: {deleted}")
    print(f"  ❌ Échecs: {failed}")
    print(f"{'='*60}\n")
    
    return converted > 0

def main():
    parser = argparse.ArgumentParser(description='Convertit tous les fichiers PNG en WebP')
    parser.add_argument('--yes', '-y', action='store_true', 
                       help='Exécuter sans demander de confirmation')
    args = parser.parse_args()
    
    print("🔄 Conversion PNG → WebP\n")
    print("Ce script va convertir tous les fichiers PNG en WebP dans le dossier images/")
    print("Les fichiers PNG originaux seront supprimés après conversion.\n")
    
    # Demander confirmation sauf si --yes est utilisé
    if not args.yes:
        try:
            response = input("Voulez-vous continuer ? (o/n): ").strip().lower()
            if response not in ('o', 'oui', 'y', 'yes'):
                print("❌ Conversion annulée")
                return
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Conversion annulée")
            return
    
    has_conversions = scan_and_convert()
    
    if has_conversions:
        print("✨ Conversion terminée!")
        print("\n💡 Vous pouvez maintenant régénérer l'index.html avec:")
        print("   python generate_index_html.py")
    else:
        print("ℹ️  Aucune conversion effectuée")

if __name__ == "__main__":
    main()

