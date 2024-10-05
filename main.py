import sys
import json
import pandas as pd
import geopandas as gpd
from geopy.distance import geodesic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel # Sert à passer du backend Python au frontend Js pour envoyer les statistiques au GUI, car il y a des soucis avec fetch()
from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from PyQt5.QtGui import QIcon
from shapely.geometry import Point

# Votre clé API Mapbox
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoiZG91c3R5biIsImEiOiJjbTFhdDFyc2UxdXU1MmtzY3NyYXUxbjVtIn0.BQEmSIxwgtozSxhD6g7i7Q"
MAPBOX_STYLE = "mapbox://styles/doustyn/cm1at50ju02bj01qo4vs34bfy"

# Charger les contours des plans d'eau depuis un fichier GeoJSON ou shapefile
water_bodies = gpd.read_file("find_water_map_files\\corrected_water_polygons.shp")

# Calculer les vitesses entre chaque point
def calculate_speed_and_transportation_modes(df, calculation_water):
    # Initialiser les listes avec une première valeur pour le premier point
    speeds = [0]  # Pas de vitesse pour le premier point
    transport_modes = ['unknown']  # Mode de transport inconnu pour le premier point
    colors = ['gray']  # Couleur par défaut pour le premier point
    total_distance_by_mode = {
        "avion": 0,
        "bateau": 0,
        "bus": 0,
        "voiture": 0,
        "à pied": 0
    }
    
    total_distance = 0
    
    def is_near_water(lat, lon, water_bodies):
        debug = False
        in_water = False

        if calculation_water:
            # Point de test
            point = Point(lon, lat)
            # Vérifier si le point est dans l'un des polygones des plans d'eau
            in_water = water_bodies.contains(point).any()

            if in_water:
                if debug:
                    print(f"Le point est dans un plan d'eau. lat : {lat} lon: {lon}") 
                in_water = True
            else:
                # print("Le point n'est pas dans un plan d'eau.")
                in_water = False

        return in_water
        
    for i in range(1, len(df)):
        # Distance entre deux points GPS (en km)
        point1 = (df.loc[i-1, 'lat'], df.loc[i-1, 'lon'])
        point2 = (df.loc[i, 'lat'], df.loc[i, 'lon'])
        distance_km = geodesic(point1, point2).km
        
        # Durée entre deux points (en heures)
        time1 = df.loc[i-1, 'timestamp']
        time2 = df.loc[i, 'timestamp']
        time_diff_hours = (time2 - time1).total_seconds()/3600
        
        if time_diff_hours > 0:
            # Vitesse en km/h
            speed_kmh = distance_km / time_diff_hours 
        else:
            speed_kmh = 0

        if is_near_water(df.loc[i, 'lat'], df.loc[i, 'lon'], water_bodies) and speed_kmh < 200:
            transport_mode = "bateau"
            color = "blue"
            total_distance_by_mode["bateau"] += distance_km
        elif speed_kmh > 2000:
            transport_mode = "erreur"
            color = "black"
            # total_distance_by_mode["avion"] += 0
            print(f"Erreur au point {i-1} to {i}: Distance = {distance_km} km, Time Diff = {time_diff_hours} hours, Speed = {speed_kmh} km/h, Point1 = {float(point1[0]), float(point1[1])} lat/lon, Point2 = {float(point2[0]), float(point2[1])} lat/long")
            # continue

        elif speed_kmh > 200:
            transport_mode = "avion"
            color = "red"
            total_distance_by_mode["avion"] += distance_km
        elif speed_kmh > 50:
            transport_mode = "voiture"
            color = "orange"
            total_distance_by_mode["voiture"] += distance_km
        elif speed_kmh > 10:
            transport_mode = "bus"
            color = "yellow"
            total_distance_by_mode["bus"] += distance_km
        else:
            transport_mode = "à pied"
            color = "green"
            total_distance_by_mode["à pied"] += distance_km
        
        speeds.append(speed_kmh)
        transport_modes.append(transport_mode)
        colors.append(color)
        total_distance += distance_km

    return speeds, transport_modes, colors, total_distance_by_mode, total_distance

# Fonction pour générer le GeoJSON
def generate_geojson(df):
    features = []

    for _, row in df.iterrows():
        # Définition des couleurs en fonction du mode de transport
        color = (
            'blue' if row['transport_mode'] == 'bateau' else
            'black' if row['transport_mode'] == 'erreur' else
            'red' if row['transport_mode'] == 'avion' else
            'orange' if row['transport_mode'] == 'voiture' else
            'yellow' if row['transport_mode'] == 'bus' else
            'green'
        )

        # Création d'une Feature pour chaque point
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['lon'], row['lat']]
            },
            "properties": {
                "description": "",
                "name": "",
                "mode": row['transport_mode'],
                "color": color
            }
        }
        features.append(feature)

    # Création du GeoJSON final
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return geojson

def generate_geojson_with_lines(locations_df):
    features = []

    for i in range(len(locations_df) - 1):
        # Récupération des coordonnées des deux points successifs
        point1 = [locations_df.iloc[i]['lon'], locations_df.iloc[i]['lat']]
        point2 = [locations_df.iloc[i + 1]['lon'], locations_df.iloc[i + 1]['lat']]

        # Définition de la couleur selon le mode de transport
        transport_mode = locations_df.iloc[i]['transport_mode']
        if transport_mode == "bateau":
            color = "blue"
        elif transport_mode == "avion":
            color = "red"
        elif transport_mode == "voiture":
            color = "orange"
        elif transport_mode == "bus":
            color = "yellow"
        elif transport_mode == "a_pied":
            color = "green"
        else:
            color = "black"

        # Création d'une Feature pour chaque ligne
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [point1, point2]  # Trajet entre deux points successifs
            },
            "properties": {
                "color": color  # Couleur selon le mode de transport
            }
        }
        features.append(feature)

    # Création du GeoJSON final
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return geojson

def filter_locations_if_time_not_increasing(locations):
    filtered_locations = []
    previous_time = None

    for loc in locations['locations']:
        if previous_time is None or loc['time'] > previous_time:
            filtered_locations.append(loc)
            previous_time = loc['time']
        # else:
        #     print(f"Current time :  {loc['time']}  & previous_time {previous_time}")
            # print(f"Delta time (actual-previous) {loc['time']-previous_time}")

    return filtered_locations

def filter_inwork(locations_df):

    # Seuils (à ajuster selon tes besoins)
    distance_threshold_km = 500  # par exemple, 500 km maximum entre deux points successifs
    time_threshold_sec = 3600  # par exemple, 1 heure minimum entre deux points successifs

    filtered_locations = []
    previous_location = None

    for location in locations_df['locations']:
        if previous_location is None:
            filtered_locations.append(location)
        else:
            # Calculer la distance en km entre deux points
            coord1 = (previous_location['lat'], previous_location['lon'])
            coord2 = (location['lat'], location['lon'])
            distance = geodesic(coord1, coord2).kilometers
            
            # Calculer la différence de temps
            time_diff = location['time'] - previous_location['time']
            
            # Appliquer les filtres de distance et de temps
            if distance < distance_threshold_km and time_diff > time_threshold_sec:
                filtered_locations.append(location)
        
        previous_location = location

    # Résultat : les données filtrées
    print(f"Nombre de points filtrés: {len(filtered_locations)}")

    return filtered_locations

def ecriture_geojson_and_json(locations_df):
                              
    # Générer le GeoJSON
    geojson_data = generate_geojson(locations_df)
    with open('json_files\\geojson_data.json', 'w') as f:
         json.dump(geojson_data, f, indent=4)


    geojson_data_lines = generate_geojson_with_lines(locations_df)
    with open('json_files\\geojson_data_lines.json', 'w') as f:
        json.dump(geojson_data_lines, f, indent=4)

    # Exemple d'affichage du GeoJSON généré
    # print(geojson_data)


# Classe Backend pour passer les données JSON à la page HTML via QWebChannel
class Backend(QObject):
    def __init__(self, total_distance, total_distance_by_mode, total_percentage_by_mode):
        super().__init__()
        self.total_distance = total_distance
        self.total_distance_by_mode = total_distance_by_mode
        self.total_percentage_by_mode = total_percentage_by_mode

    @pyqtSlot(result=str)
    def getTransportStats(self):
        return json.dumps({
            'total_distance': self.total_distance,
            'total_distance_by_mode': self.total_distance_by_mode,
            'total_percentage_by_mode': self.total_percentage_by_mode
        })
    
# Classe principale pour l'application PyQt5
class MapWindow(QMainWindow):
    def __init__(self, total_distance, total_distance_by_mode, total_percentage_by_mode):
        super().__init__()

        # Créer une vue Web pour afficher la carte
        self.browser = QWebEngineView()

        # Configurer le QWebChannel pour la communication entre Python et JavaScript
        self.channel = QWebChannel()
        self.backend = Backend(total_distance, total_distance_by_mode, total_percentage_by_mode)
        self.channel.registerObject('backend', self.backend)

        self.browser.page().setWebChannel(self.channel)
        self.browser.setUrl(QUrl("file:///map.html"))

        # Mettre la vue Web dans la fenêtre principale
        print_mapbox = True
        if print_mapbox:
            self.setCentralWidget(self.browser)
            self.setWindowTitle("Polarsteps2stats")
            self.resize(1000, 800)
            self.setWindowIcon(QIcon('images/favicon.ico'))
            

def main():
    # Charger les données JSON
    # with open('json_files\\trip.json', 'r') as trip_file:
    #     trip_data = json.load(trip_file)

    # with open('simplified_locations.json', 'r') as locations_file:
    #     locations_data = json.load(locations_file)
    # print('simplified_locations.json loaded.')

    with open('json_files\\locations.json', 'r') as locations_file:
        locations_data = json.load(locations_file)
    print(f"Length locations_data before time filter: {len(locations_data['locations'])}")

    # Trier selon le champ 'time'
    locations_data = locations_data['locations']
    locations_data.sort(key=lambda x: x['time'])
    locations_data = {"locations":locations_data}
    locations_data = filter_locations_if_time_not_increasing(locations_data)
    locations_data = {"locations":locations_data}
    print(f"Length locations_data after time filter: {len(locations_data['locations'])}")

    # Convertir en DataFrame
    locations_df = pd.DataFrame(locations_data['locations'])

    # filtered_locations = filter_inwork(locations_df)

    # Convertir les timestamps en datetime
    locations_df['timestamp'] = pd.to_datetime(locations_df['time'], unit='s')

    # Extraire les coordonnées lat/lon
    locations_df['lat'] = locations_df['lat']
    locations_df['lon'] = locations_df['lon']

    # Appliquer la fonction pour calculer les vitesses, modes de transport, et les couleurs
    (locations_df['speed'],
     locations_df['transport_mode'], 
     locations_df['color'],
     total_distance_by_mode, 
     total_distance) = calculate_speed_and_transportation_modes(locations_df,calculation_water = False)

    total_percentage_by_mode = {mode: total_distance_by_mode[mode] / total_distance * 100 for mode in total_distance_by_mode}

    # # Sauvegarder le DataFrame en CSV
    # locations_df.to_csv('locations_df.csv', index=False)
       
    ecriture_geojson_and_json(locations_df)

    # Lancement de l'application PyQt5
    app = QApplication(sys.argv)
    window = MapWindow(total_distance, total_distance_by_mode, total_percentage_by_mode)
    window.show()
    sys.exit(app.exec_())

# Exécuter le script principal uniquement si ce fichier est exécuté directement
if __name__ == '__main__':
    main()
