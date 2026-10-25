# FoxCat HeatBuilding

Intégration personnalisée Home Assistant pour la gestion thermique d'un bâtiment,
la présence et l'optimisation solaire/tarifaire.

## État de la version

`1.0.0-beta.1` est un squelette fonctionnel orienté observation et simulation.
Le contrôle physique des équipements n'est volontairement pas implémenté.
L'interrupteur « Autoriser le moteur automatique » active uniquement le drapeau
du moteur ; il n'envoie aucune commande aux appareils.

## Installation manuelle

1. Copier le dossier `custom_components/foxcat_heatbuilding` dans le dossier
   `custom_components` de Home Assistant.
2. Redémarrer Home Assistant.
3. Aller dans **Paramètres → Appareils et services → Ajouter une intégration**.
4. Rechercher **FoxCat HeatBuilding** et compléter le formulaire.

## Configuration actuelle

- Nom du bâtiment.
- Identifiants de zones (liste séparée par des virgules).
- Entités `person.*`.
- Température extérieure, puissance solaire, puissance réseau, prix et météo.
- Intervalle de collecte de 15 à 600 secondes.

La première version ne permet pas encore d'associer un capteur de température
et un équipement `climate` à chaque zone depuis le formulaire. Les zones sont
des entrées de registre et les diagnostics globaux permettent de valider
l'installation avant d'ajouter le configurateur de zone.

## Sécurité

- Aucune automatisation existante n'est modifiée.
- Aucun service HVAC n'est appelé.
- L'exécution physique est bloquée dans cette version.
- L'optimisation solaire exige de vérifier le sens de signe du capteur réseau.
- Les valeurs de consigne et paramètres affichés sont des exemples de départ,
  pas des recommandations universelles.

## Développement

Installer les dépendances de test dans un environnement de développement
compatible avec la version Home Assistant ciblée, puis exécuter :

```bash
pytest -q
```

Avant toute activation de commandes physiques, il faudra ajouter :
- le configurateur de zone (capteur de température et entité climate explicites) ;
- les limites propres à chaque équipement ;
- la détection des conflits d'automatisations ;
- la vérification du mode HVAC et des unités ;
- un journal des commandes, une temporisation et un mécanisme de repli ;
- des tests d'intégration avec Home Assistant.
