import json

with open('locations.json', 'r') as locations_file:
    locations_data = json.load(locations_file)
print('locations.json loaded.')

def filter_locations(locations):
    filtered_locations = []
    previous_time = None

    for loc in locations['locations']:
        if previous_time is None or loc['time'] > previous_time:
            filtered_locations.append(loc)
            previous_time = loc['time']
        # else:
        #     print(f"Current time :  {loc['time']}  & previous_time {previous_time}")
        #     print(f"Delta time (actual-previous) {loc['time']-previous_time}")

    return filtered_locations

filtered_locations = filter_locations(locations_data)
filtered_locations = {"locations": filtered_locations}
print(filtered_locations)


import pandas as pd
from geopy.distance import geodesic

# Charger les données depuis le fichier JSON
df = pd.read_json("/mnt/data/locations.json")
locations = df['locations']

# Seuils (à ajuster selon tes besoins)
distance_threshold_km = 500  # par exemple, 500 km maximum entre deux points successifs
time_threshold_sec = 3600  # par exemple, 1 heure minimum entre deux points successifs

filtered_locations = []
previous_location = None

for location in locations:
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
