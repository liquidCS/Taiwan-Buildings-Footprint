import matplotlib.pyplot as plt
import pyrosm 
import math
from shapely.geometry import  Polygon, box
import sys 
import contextily as cx 
import geopandas
import folium


x, y, z = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])





def tile2bbox(x, y, z):
    n = 2 ** z
    min_lon = x / n * 360.0 - 180.0
    max_lon = (x + 1) / n * 360.0 - 180.0

    max_lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    min_lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))

    return min_lon, min_lat, max_lon, max_lat  

def bbox2polygon(min_lon, min_lat, max_lon, max_lat):
    return [
        [min_lon, min_lat],  # lower-left
        [max_lon, min_lat],  # lower-right
        [max_lon, max_lat],  # upper-right
        [min_lon, max_lat],  # upper-left
        [min_lon, min_lat],  # close ring
    ]



osm = pyrosm.OSM("../Taiwan-Buildings-Footprint/pbf/county/A.pbf")


# Calculate the bbox of a single tile
min_lon, min_lat, max_lon, max_lat = tile2bbox(x, y, z)
gdf = geopandas.GeoSeries([box(min_lon, min_lat, max_lon, max_lat)], crs="EPSG:4326")
gdf_3857 = gdf.to_crs(epsg=3857)
minx, miny, maxx, maxy = gdf_3857.total_bounds


# === Annotated images using OSM data === 

fig, ax = plt.subplots(1, 1, figsize=(2.56, 2.56))
fig.set_facecolor('black')
ax.set_axis_off()

# Limit the output area
ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)

# Add buildings to plot
buildings = osm.get_buildings().to_crs(epsg=3857)
buildings.plot(ax=ax, color='white', edgecolor='black', linewidth=0.5, antialiased=False)


fig.subplots_adjust(left=0, right=1, top=1, bottom=0) # make margin smaller
plt.savefig(f"data/train_masks/Buildings/{x}-{y}-{z}.png")


# === train images ===

fig, ax = plt.subplots(1, 1, figsize=(2.56, 2.56))
fig.set_facecolor('black')
ax.set_axis_off()

ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)

cx.add_basemap(ax, attribution_size=0, source="https://wmts.nlsc.gov.tw/wmts/PHOTO2/default/EPSG:3857/{z}/{y}/{x}", zoom=z) # Add basemap

fig.subplots_adjust(left=0, right=1, top=1, bottom=0) # make margin smaller
plt.savefig(f"data/train_images/{x}-{y}-{z}.png")

