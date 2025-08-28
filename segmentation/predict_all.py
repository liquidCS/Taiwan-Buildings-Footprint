import sys
sys.path.append("..")
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import cv2
import matplotlib.pyplot as plt
import numpy as np
import requests
import argparse 
from pyproj import Transformer
from shapely.geometry import Polygon
import json


parser = argparse.ArgumentParser(description="Generate building boundaries prediction using satellite tiles.")
parser.add_argument("x", type=int, help='x - WMP horizontal tile index')
parser.add_argument("y", type=int, help='y - WMP vertical tile index')
parser.add_argument("z", type=int, help='z - WMP zoom level')
parser.add_argument('--url', type=str, help='The URL for WMTS satellite tiles' )
args = parser.parse_args()

# Model settings
sam_checkpoint = "sam_vit_h_4b8939.pth"
model_type = "vit_h"

# Fetching image tile
if args.url == None:
    url = f"https://wmts.nlsc.gov.tw/wmts/PHOTO2/default/EPSG:3857/{args.z}/{args.y}/{args.x}"
response = requests.get(url)
image_array = np.asarray(bytearray(response.content), dtype=np.uint8)


def show_anns(anns):
    """
    Display the segmentation result.
    Loop through all result and display it on image.
    """
    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    ax = plt.gca()
    ax.set_autoscale_on(False)

    img = np.ones((sorted_anns[0]['segmentation'].shape[0], sorted_anns[0]['segmentation'].shape[1], 4))
    img[:,:,3] = 0
    for ann in sorted_anns:
        m = ann['segmentation']
        color_mask = np.concatenate([np.random.random(3), [0.35]])
        img[m] = color_mask
    ax.imshow(img)


def masks_to_geojson(masks, x_tile, y_tile, z_tile, image_shape):
    """
    Converts a list of masks to a GeoJSON FeatureCollection with lat/lon coordinates.
    Args:
        masks (list): A list of dictionaries, each containing a 'segmentation' boolean array.
        x_tile (int): The x tile index (Web Mercator).
        y_tile (int): The y tile index (Web Mercator).
        z_tile (int): The zoom level (Web Mercator).
        image_shape (tuple): The shape of the image (height, width, channels).
    Returns:
        dict: A GeoJSON FeatureCollection.
    """
    features = []
    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

    # Calculate Web Mercator bounding box for the tile
    n = 2 ** z_tile
    R = 6378137 # Earth radius in meters
    
    # Calculate longitude (x) bounds
    lon_rad_left = (x_tile / n) * 2 * np.pi - np.pi
    lon_rad_right = ((x_tile + 1) / n) * 2 * np.pi - np.pi

    min_x_merc = R * lon_rad_left
    max_x_merc = R * lon_rad_right

    # Calculate latitude (y) bounds
    # y_tile increases from north to south in standard Web Mercator tile systems.
    # Web Mercator y-coordinate increases from south to north.
    # So, y_tile corresponds to the top (north) edge, and y_tile + 1 corresponds to the bottom (south) edge.
    lat_rad_top = np.arctan(np.sinh(np.pi * (1 - 2 * y_tile / n)))
    lat_rad_bottom = np.arctan(np.sinh(np.pi * (1 - 2 * (y_tile + 1) / n)))

    max_y_merc = R * lat_rad_top # Northmost (highest Y) Web Mercator coordinate
    min_y_merc = R * lat_rad_bottom # Southmost (lowest Y) Web Mercator coordinate

    image_height, image_width, _ = image_shape

    for mask_data in masks:
        segmentation = mask_data['segmentation']
        
        # Find contours from the binary mask
        contours, _ = cv2.findContours(segmentation.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if contour.shape[0] < 3: # A polygon needs at least 3 points
                continue
            
            # Convert pixel coordinates to Web Mercator
            mercator_coords = []
            for point in contour.squeeze():
                px, py = point[0], point[1]
                
                # Scale pixel x-coordinate to Web Mercator x
                mx = min_x_merc + (px / image_width) * (max_x_merc - min_x_merc)
                # Scale pixel y-coordinate to Web Mercator y (invert y-axis for pixel to mercator)
                my = max_y_merc - (py / image_height) * (max_y_merc - min_y_merc)
                mercator_coords.append((mx, my))
            
            if not mercator_coords:
                continue

            # Create a shapely Polygon
            try:
                polygon = Polygon(mercator_coords)
            except Exception as e:
                print(f"Could not create polygon from mercator_coords: {mercator_coords}. Error: {e}")
                continue

            if polygon.is_empty:
                continue

            # Convert Web Mercator to Lat/Lon
            lonlat_coords = []
            # For exterior ring
            for mx, my in polygon.exterior.coords:
                lon, lat = transformer.transform(mx, my)
                lonlat_coords.append((lon, lat))
            
            # Handle interior rings (holes)
            interior_rings_lonlat = []
            for interior_ring in polygon.interiors:
                ring_coords = []
                for mx, my in interior_ring.coords:
                    lon, lat = transformer.transform(mx, my)
                    ring_coords.append((lon, lat))
                interior_rings_lonlat.append(ring_coords)

            # GeoJSON format requires exterior ring first, then interior rings
            geojson_polygon_coords = [lonlat_coords] + interior_rings_lonlat

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": geojson_polygon_coords
                },
                "properties": {
                    "area": mask_data.get('area'),
                    "bbox": mask_data.get('bbox')
                }
            }
            features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }


image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)

mask_generator = SamAutomaticMaskGenerator(sam)


masks = mask_generator.generate(image)


print(f"Generated {len(masks)} masks.")
# print(masks[0].keys()) # Uncomment to see mask keys if needed

# Convert masks to GeoJSON
geojson_output = masks_to_geojson(masks, args.x, args.y, args.z, image.shape)

# Save GeoJSON output
with open("output.geojson", 'w') as file:
    json.dump(geojson_output, file)

# Optional: Save GeoJSON to a file
# with open(f"masks_tile_{args.x}_{args.y}_{args.z}.geojson", "w") as f:
#     json.dump(geojson_output, f, indent=2)
# print(f"GeoJSON saved to masks_tile_{args.x}_{args.y}_{args.z}.geojson")


plt.figure(figsize=(20,20))
plt.imshow(image)
show_anns(masks)
plt.axis('off')
plt.show()
