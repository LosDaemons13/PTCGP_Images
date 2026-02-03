#!/usr/bin/env python3
"""Convertit les liens images pokekalos vers PTCGP_Images (GitHub Pages)."""

import json
import re
from pathlib import Path

BASE_URL = "https://losdaemons13.github.io/PTCGP_Images"
JSON_PATH = Path(__file__).parent / "pokemon_cards_fr.json"


def extract_set_code(set_details: str) -> str | None:
    """Extrait le code set des parenthèses, ex: 'Fantastical Parade  (B2)' -> 'B2'."""
    if not set_details:
        return None
    m = re.search(r"\(([A-Za-z0-9]+)\)\s*$", set_details.strip())
    return m.group(1) if m else None


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    converted = 0
    skipped = 0
    for card in cards:
        old_url = card.get("image", "")
        if "media.pokekalos.fr" not in old_url:
            skipped += 1
            continue
        set_details = card.get("set_details", "")
        set_code = extract_set_code(set_details)
        id_set = card.get("id_set", "")
        if not set_code or not id_set:
            skipped += 1
            continue
        try:
            num = int(id_set)
        except (ValueError, TypeError):
            skipped += 1
            continue
        filename = f"{set_code}_{num:03d}_FR.webp"
        new_url = f"{BASE_URL}/images/{set_code}/{filename}"
        card["image"] = new_url
        converted += 1

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=4)

    print(f"Liens convertis : {converted}")
    if skipped:
        print(f"Entrées ignorées : {skipped}")


if __name__ == "__main__":
    main()
