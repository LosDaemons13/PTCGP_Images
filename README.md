# PTCGP_Images

Images de cartes **Pokémon TCG Pocket** en **français (FR)** et **anglais (EN)**, servies
via GitHub Pages pour le site FrenchRerollers (remplace l'ancien repo `losdaemons13/PTCGP_Images`, supprimé).

## Structure

```
images/{SET}/{SET}_{NUM}_{LANG}.webp
```

- `{SET}` : code du set (`A1`, `A1a`, … `C1`).
- `{NUM}` : numéro de carte zéro-paddé sur 3 chiffres (`001`).
- `{LANG}` : `FR` ou `EN`.

Exemple : [`images/A1/A1_001_FR.webp`](images/A1/A1_001_FR.webp)

## Utilisation

Une fois GitHub Pages activé (Settings → Pages → branche `main`, dossier `/root`) :

```
https://<pseudo>.github.io/PTCGP_Images/images/A1/A1_001_FR.webp
```

## Sources

- **EN** : miroir public Limitless TCG (les 23 sets).
- **FR (sets anciens, A1–A4)** : TCGdex (`assets.tcgdex.net`, multi-langues).
- **FR (sets récents)** : extraits des assets du jeu (CDN Takasho) — seule source FR complète.

Les artworks sont la propriété de Nintendo / Creatures / GAME FREAK. Redistribution à usage
communautaire (fan-site FrenchRerollers), non affiliée à The Pokémon Company.
