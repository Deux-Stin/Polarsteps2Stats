import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

water_bodies = gpd.read_file("C:\\Users\\User\\Downloads\\water-polygons-split-4326\\water-polygons-split-4326\\water_polygons.shp")

# Simplifier la géométrie pour réduire la complexité (le paramètre tolerance peut être ajusté)
simplified_water_bodies = water_bodies.simplify(tolerance=0.01)

# # Sauvegarder le fichier simplifié pour un usage ultérieur
# simplified_water_bodies.to_file("simplified_water_polygons.shp")

# Vérification du fichier simplifié
print(simplified_water_bodies)

# Charger le fichier shapefile
water_bodies = simplified_water_bodies

# Fonction pour corriger les polygones avec un winding order invalide
def correct_winding_order(geometry):
    if isinstance(geometry, Polygon):
        if not geometry.is_valid:
            geometry = geometry.buffer(0)  # Corriger les géométries invalides
        return geometry
    elif isinstance(geometry, MultiPolygon):
        # Assurer que chaque polygone dans le MultiPolygon est valide
        valid_polygons = [poly if poly.is_valid else poly.buffer(0) for poly in geometry.geoms]
        return MultiPolygon(valid_polygons)
    return geometry

# Appliquer la correction sur chaque géométrie
water_bodies['geometry'] = water_bodies['geometry'].apply(correct_winding_order)

# Sauvegarder le fichier corrigé
water_bodies.to_file("corrected_water_polygons.shp")
