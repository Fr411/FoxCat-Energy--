# FoxCat Heating

Intégration personnalisée Home Assistant pour estimer le temps de montée en température d'une pièce chauffée par une unité CVC.

## Fonctions
- Configurateur UI par pièce : dimensions, volume, entité `climate`, sonde intérieure et sonde extérieure.
- Lecture de `fan_mode` et `fan_modes`.
- Débit par vitesse : valeur personnalisée par mode si renseignée ; sinon estimation linéaire par rang, du débit maximal divisé par N jusqu'au débit maximal.
- Estimation de puissance thermique, pertes, énergie nécessaire et temps de chauffe.
- Courbe optionnelle de correction de puissance selon la température extérieure.
- Entités regroupées dans un appareil par pièce.

## Installation manuelle
1. Copier `custom_components/foxcat_heating` dans le dossier `config/custom_components/` de Home Assistant.
2. Vérifier que le chemin final est `config/custom_components/foxcat_heating/manifest.json`.
3. Redémarrer Home Assistant.
4. Aller dans **Paramètres → Appareils et services → Ajouter une intégration → FoxCat Heating**.
5. Créer une configuration pour chaque pièce.

## Capteurs
Les capteurs créés portent les noms :
- Temps de chauffe estimé
- Débit de ventilation estimé
- Puissance thermique estimée
- Puissance nette estimée
- Énergie thermique estimée nécessaire
- Déperditions thermiques estimées
- Surface configurée
- Volume configuré
- Écart à la consigne
- État du calcul

Le préfixe d'entité dépend du nom de pièce configuré. Les identifiants exacts sont générés par Home Assistant à partir du nom de l'appareil et des entités.

## Configuration avancée
Dans les options de l'intégration, les deux champs JSON permettent d'affiner les débits et la puissance :
- Débits par vitesse : `{"Quiet": 180, "Medium": 350, "High": 500}`
- Facteurs de puissance extérieure : `{"-15": 0.55, "-7": 0.70, "2": 0.88, "7": 1.0, "12": 1.0}`

Le facteur de la courbe est interpolé linéairement entre les points et borné à la plage de la courbe aux extrémités. La courbe est désactivée par défaut : les facteurs d'exemple ne doivent pas être considérés comme des données constructeur.

## Limites physiques à lire avant usage
- Le débit d'air n'est pas une puissance thermique. La relation entre vitesse du ventilateur et puissance restituée n'est pas linéaire. Le débit par rang est uniquement une approximation de repli.
- Le calcul applique une pénalité de ventilation volontairement limitée (`0,70 + 0,30 × débit relatif`) pour éviter d'assimiler directement le débit à la puissance thermique. Cette loi est heuristique, pas une loi constructeur ; calibrer ou remplacer par des puissances mesurées.
- La capacité thermique effective (kWh/K) et le coefficient de déperdition (kW/K) sont à calibrer avec l'historique réel. Les valeurs par défaut sont illustratives.
- Les données de puissance min/max ne modélisent pas la régulation du compresseur ; la puissance disponible est estimée à partir de la puissance nominale et du facteur extérieur.
- La prévision ne pilote pas la climatisation. Cette intégration est strictement en lecture et calcul.
- Une estimation nulle signifie consigne atteinte. Une valeur indisponible indique des données manquantes ou une puissance nette non positive.
- Vérifier les attributs réellement exposés par l'intégration du climatiseur : certaines intégrations ne publient pas `fan_modes` ou `fan_mode` de manière standard.

## Validation
Cette archive est une première version de développement. Tester la configuration sur une instance de test, vérifier les logs Home Assistant et comparer les estimations à des séquences de chauffe mesurées avant de s'appuyer dessus pour des décisions énergétiques.
