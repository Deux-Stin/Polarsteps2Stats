from geopy.distance import geodesic
import json
import pandas as pd

with open('locations.json', 'r') as locations_file:
    locations_data = json.load(locations_file)
print('locations.json loaded.')


# Extract GPS positions and timestamps from the subset data
locations = locations_data['locations']
distances = []
time_intervals = []
incoherences = []

# Convertir en DataFrame
locations_df = pd.DataFrame(locations_data['locations'])
locations_df['timestamp'] = pd.to_datetime(locations_df['time'], unit='s')

# Calculate distances between consecutive points and time intervals
for i in range(1, len(locations)):
    pos1 = (locations[i-1]['lat'], locations[i-1]['lon'])
    pos2 = (locations[i]['lat'], locations[i]['lon'])
    
    # Calculate geodesic distance (in kilometers)
    distance = geodesic(pos1, pos2).kilometers
    distances.append(distance)
    
    # Calculate time difference (in seconds)
    time_interval = locations[i]['time'] - locations[i-1]['time'] # En secondes
    time_intervals.append(time_interval)
    
    # Check for incoherence: large distance over a short time
    if distance > 1000 and time_interval < 6000:  # Example: more than 10 km in less than 1 minutes
        incoherences.append((i-1, i, distance, time_interval))

# Create a summary of findings
subset_incoherence_summary = {
    "distances_km": distances,
    "time_intervals_sec": time_intervals,
    "incoherences": incoherences
}

subset_incoherence_summary

print(incoherences)

# Dénombrer les incohérences avec un time_interval négatif
count_negative_time_intervals = sum(1 for _, _, _, time_interval in incoherences if time_interval < 0)

print("Nombre d'incohérences avec un time_interval négatif:", count_negative_time_intervals)