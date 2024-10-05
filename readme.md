# Polarsteps2Stats

**Polarsteps2Stats** est une application Python interactive qui permet d'analyser et de visualiser des données GPS de voyages sur une carte Mapbox. Elle calcule des statistiques basées sur les modes de transport et affiche les résultats de manière graphique et textuelle dans une interface utilisateur développée avec PyQt5.

## Fonctionnalités principales

### 1. **Affichage interactif sur Mapbox**
   - Visualisation des points GPS sur une carte 3D avec projection globe.
   - Trajets reliés par des lignes de couleur représentant les différents modes de transport.
   - Affichage de popups interactifs lors du clic sur un point GPS, avec des détails comme les coordonnées et les descriptions.

### 2. **Modes de transport différenciés par couleurs**
   - Les trajets sont colorés en fonction du mode de transport :
     - ✈️ **Avion** (Rouge)
     - 🛥️ **Bateau** (Bleu)
     - 🚌 **Bus** (Jaune)
     - 🚗 **Voiture** (Orange)
     - 🚶 **À pied** (Vert)

### 3. **Calcul et affichage des statistiques de trajet**
   - **Distance totale parcourue** affichée dans un encart à droite de la carte.
   - **Détail des distances par mode de transport**, incluant les distances en kilomètres et les pourcentages de chaque mode de transport par rapport à la distance totale.
   - Calcul en temps réel des statistiques à partir des données GPS.

### 4. **Gestion des anomalies et filtrage**
   - Filtrage des points GPS pour éliminer les incohérences temporelles (timestamps non croissants).
   - Suppression des points GPS trop éloignés spatialement ou temporellement pour garantir un tracé cohérent.

### 5. **Navigation avec les touches du clavier**
   - Utilisation des flèches du clavier pour sauter d’un point GPS à l’autre et explorer les différentes étapes du voyage.

### 6. **Sauvegarde des données**
   - Génération automatique des fichiers GeoJSON contenant les informations des points et des lignes de trajet.
   - Sauvegarde des statistiques dans un fichier JSON pour une réutilisation ou analyse ultérieure.

## Prérequis

- Python 3.x
- PyQt5
- Pandas
- Geopy
- Mapbox Access Token
- Geopandas
- Shapely

## Installation

1. Clonez le repository sur votre machine locale :
   ```bash
   git clone https://github.com/Deux-Stin/Polarsteps2Stats.git

2. Installez les dépendances requises :
    ```bash
    pip install -r requirements.txt

3. Ajoutez votre clé API Mapbox dans le fichier main.py :
    MAPBOX_ACCESS_TOKEN = "votre_clé_mapbox"

4. Lancez l'application :
    ```bash
    python main.py


### Utilisation

- Visualisez les points GPS sur la carte et les statistiques de trajet dans l'encart à droite.
- Utilisez les flèches du clavier pour naviguer d’un point à un autre.
- Les fichiers GeoJSON et JSON générés peuvent être trouvés dans le sous-répertoire du projet /json_files.

© 2024 Polarsteps2Stats. Tous droits réservés.