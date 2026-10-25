# FoxCat HeatBuilding

Intégration personnalisée Home Assistant pour la gestion thermique d'un bâtiment,
la présence et l'optimisation solaire/tarifaire.

## Installation via HACS

1. Dans HACS, ouvrez **Intégrations** puis le menu **⋮ → Dépôts personnalisés**.
2. Ajoutez `https://github.com/Fr411/FoxCat-Energy--` avec la catégorie **Intégration**.
3. Recherchez **FoxCat HeatBuilding**, installez l'intégration puis redémarrez Home Assistant.
4. Ajoutez **FoxCat HeatBuilding** depuis **Paramètres → Appareils et services**.

Une nouvelle release GitHub doit être publiée avec le tag `0.1.3` pour que HACS
puisse installer cette version. Le numéro de version dans `manifest.json` doit
correspondre au tag de la release.

## Installation manuelle

Copier `custom_components/foxcat_heatbuilding` dans le dossier
`custom_components` de Home Assistant, redémarrer Home Assistant, puis ajouter
l'intégration depuis **Paramètres → Appareils et services**.

## Configuration actuelle

- Nom du bâtiment et identifiants de zones (liste séparée par des virgules).
- Entités `person.*`.
- Température extérieure, puissance solaire, puissance réseau, prix et météo.
- Intervalle de collecte de 15 à 600 secondes.

Les zones sont des entrées de registre ; le configurateur de zone permettant
d'associer une sonde et une entité `climate` n'est pas encore disponible.

## Sécurité et limites

- Aucune automatisation existante n'est modifiée et aucun service HVAC n'est appelé.
- L'exécution physique est bloquée ; l'interrupteur automatique ne fait qu'activer
  le drapeau du moteur.
- Les valeurs et paramètres affichés sont des exemples à calibrer, pas des
  recommandations universelles.
- Vérifier le sens du capteur réseau avant d'utiliser l'optimisation solaire.

## Développement

Exécuter les tests avec `pytest -q` dans un environnement compatible avec la
version Home Assistant ciblée.
