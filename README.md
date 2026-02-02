# SmartCare Analytics

Base de projet pour explorer l'analytics autour de SmartCare. Le depot est un squelette Python minimal pret a accueillir ingestion et traitement de donnees (sante, IOT, etc.).

## Prerequis
- Python 3.13
- Git

## Installation rapide
```bash
python3.13 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt  # optionnel, si un fichier est ajoute
```

## Lancer la demo
```bash
python main.py
```

## Structure
- `main.py` : point d'entree actuel (affiche un message de bienvenue).
- `pyproject.toml` : metadonnees du projet; a enrichir avec dependances et systeme de build.
- `.gitignore` : exclusions courantes Python.

## Prochaines etapes suggerees
- Definir les cas d'usage analytics (indicateurs, dashboards, alertes).
- Choisir la stack data (pandas/Polars, stockage, visualisation).
- Ajouter les dependances et le systeme de build dans `pyproject.toml`.
- Mettre en place des tests et une CI basique.

## Contribution
1. Creer une branche (`git checkout -b feature/...`).
2. Commiter des changements clairs et petits.
3. Ouvrir une pull request vers `main`.
