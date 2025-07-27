import subprocess 
import os
import warnings
import zipfile
import geopandas 
import json
import subprocess
import pyrosm
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

## Setting

county_id = 'O'
warnings.simplefilter("ignore")



## Fucntions

def MakeSureDirExist(path):
    if not os.path.exists(path):
        os.makedirs(path)




## Data Prepareing
img_path = './out/img'
MakeSureDirExist(img_path)

shp_path = './shp/'
MakeSureDirExist(shp_path)
pbf_path = './pbf/'
MakeSureDirExist(pbf_path)
geoJson_path = './geojsons'
MakeSureDirExist(geoJson_path)

download_files = [
    {'path': './shp/county_boundaries.zip', 'url': 'https://data.depositar.io/en/dataset/5fae1054-c9d5-409b-96ab-e2bd4da20960/resource/2ad90c25-8c62-42d7-8649-15b107252c52/download/county_boundaries.zip'},
    {'path': './shp/town_boundaries.zip', 'url': 'https://data.depositar.io/en/dataset/5fae1054-c9d5-409b-96ab-e2bd4da20960/resource/c714accb-70f1-45ec-a51d-ce0ef2c81a72/download/town_boundaries.zip'},
    {'path': './shp/village_boundaries.zip', 'url': 'https://data.depositar.io/en/dataset/5fae1054-c9d5-409b-96ab-e2bd4da20960/resource/a44035e1-d829-45fb-8ec5-1f425d3c8cab/download/village_boundaries.zip'},
    {'path': './pbf/taiwan.osm.pbf', 'url': 'https://data.depositar.io/en/dataset/5fae1054-c9d5-409b-96ab-e2bd4da20960/resource/1234dee7-323f-459c-b719-3437bfcb96f3/download/taiwan-20250717.osm.pbf'}
]

for i in range(len(download_files)):
    if not os.path.exists(download_files[i]['path']):
        command = ['curl', '-L', '-o', download_files[i]['path'], download_files[i]['url']]
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stderr)



## .shp Data Processing

county_shp_path = './shp/county_boundaries' # Extract county boundaries
town_shp_path = './shp/town_boundaries' # Extract town boundaries
village_shp_path = './shp/village_boundaries' # Extract village boundaries

MakeSureDirExist(county_shp_path)
MakeSureDirExist(town_shp_path)
MakeSureDirExist(village_shp_path)

if not os.path.exists(f'{county_shp_path}/COUNTY_MOI_1140318.shp'):
    with zipfile.ZipFile('./shp/county_boundaries.zip', 'r') as zip_ref: # Extract all files in zip to path
        zip_ref.extractall(county_shp_path)

if not os.path.exists(f'{town_shp_path}/TOWN_MOI_1140318.shp'):
    with zipfile.ZipFile('./shp/town_boundaries.zip', 'r') as zip_ref:
        zip_ref.extractall(town_shp_path)

if not os.path.exists(f'{village_shp_path}/VILLAGE_NLSC_1140620.shp'):
    with zipfile.ZipFile('./shp/village_boundaries.zip', 'r') as zip_ref: 
        zip_ref.extractall(village_shp_path)


## geoJson Data Processing

county_geoJson_path = './geojsons/county_boundaries.geojson'
town_geoJson_path = './geojsons/town_boundaries.geojson'
village_geoJson_path = './geojsons/village_boundaries.geojson'

for file in os.listdir(county_shp_path): # find the correct shp file
    if file.endswith('.shp'):
        county_shapefile = os.path.join(county_shp_path, file)
        break

for file in os.listdir(town_shp_path):
    if file.endswith('.shp') and file.startswith('TOWN_MOI'):
        town_shapefile = os.path.join(town_shp_path, file)
        break

for file in os.listdir(village_shp_path):
    if file.endswith('.shp') and file.startswith('VILLAGE'):
        village_shapefile = os.path.join(village_shp_path, file)
        break


if not os.path.exists(f'{geoJson_path}/county_boundaries.geojson'):
    county_shp_data = geopandas.read_file(county_shapefile) # Convert shp to geojson 
    county_shp_data.to_file(county_geoJson_path, driver='GeoJSON')  

if not os.path.exists(f'{geoJson_path}/town_boundaries.geojson'):
    town_shp_data = geopandas.read_file(town_shapefile)
    town_shp_data.to_file(town_geoJson_path, driver='GeoJSON')

if not os.path.exists(f'{geoJson_path}/village_boundaries.geojson'):
    village_shp_data = geopandas.read_file(village_shapefile)
    village_shp_data.to_file(village_geoJson_path, driver='GeoJSON')


## Geojson Break Down 


with open(f'{geoJson_path}/county_boundaries.geojson', 'r') as file: # Break down county geojson
    data = json.load(file)

MakeSureDirExist(f'{geoJson_path}/county')
for county in data['features']:
    if county['properties']['COUNTYID'] == county_id:
        if not os.path.exists(f"{geoJson_path}/county/{county['properties']['COUNTYID']}.geojson"): 
            with open(f"{geoJson_path}/county/{county['properties']['COUNTYID']}.geojson", 'w+') as file:
                json.dump(county, file)


with open(f'{geoJson_path}/town_boundaries.geojson', 'r') as file:
    data = json.load(file)

MakeSureDirExist(f'{geoJson_path}/town')
for town in data['features']:
    if town['properties']['COUNTYID'] == county_id:
        if not os.path.exists(f"{geoJson_path}/town/{town['properties']['TOWNID']}.geojson"): 
            with open(f"{geoJson_path}/town/{town['properties']['TOWNID']}.geojson", 'w+') as file:
                json.dump(town, file)


with open(f'{geoJson_path}/village_boundaries.geojson', 'r') as file:
    data = json.load(file)

MakeSureDirExist(f'{geoJson_path}/village/')
for village in data['features']:
    if village['properties']['COUNTYID'] == county_id: 
        if not os.path.exists(f"{geoJson_path}/village/{village['properties']['VILLCODE']}.geojson"): 
            with open(f"{geoJson_path}/village/{village['properties']['VILLCODE']}.geojson", 'w+') as file:
                json.dump(village, file)


## .pbf Break Down

MakeSureDirExist(f'./pbf/county/') # Break down pbf to county level
command = ['osmium', 'extract', '-p', f'./geojsons/county/{county_id}.geojson', f'./pbf/taiwan.osm.pbf', '-o', f'./pbf/county/{county_id}.pbf', '--overwrite']
result = subprocess.run(command, capture_output=True, text=True)

MakeSureDirExist(f'./pbf/town')
boundaries = geopandas.read_file(town_geoJson_path) # Break to town level 
town_boundaries = boundaries[boundaries['COUNTYID'] == county_id]
for town_boundary in town_boundaries.iterfeatures():
    town_id = town_boundary['properties']['TOWNID']
    
    if not os.path.exists(f'./pbf/town/{town_id}.pbf'):
        command = ['osmium', 'extract', '-p', f'./geojsons/town/{town_id}.geojson', f'./pbf/county/{county_id}.pbf', '-o', f'./pbf/town/{town_id}.pbf', '--overwrite']
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stderr)
        print(result.stdout)


MakeSureDirExist(f'./pbf/village/')
boundaries = geopandas.read_file(village_geoJson_path)
village_boundaries = boundaries[boundaries['COUNTYID'] == county_id]
for village_boundary in village_boundaries.iterfeatures():
    village_id = village_boundary['properties']['VILLCODE']
    town_id = village_boundary['properties']['TOWNID']

    if not os.path.exists(f'./pbf/village/{village_id}.pbf'):
        command = ['osmium', 'extract', '-p', f'./geojsons/village/{village_id}.geojson', f'./pbf/town/{town_id}.pbf', '-o', f'./pbf/village/{village_id}.pbf', '--overwrite']
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stderr)
        print(result.stdout)






## Start Plotting grtaph fucntion

def GenImgBuildingPlot():
    print("Running Building Image...")

    osm = pyrosm.OSM(f'./pbf/county/{county_id}.pbf')

    fig, ax = plt.subplots(1, 1, figsize=(100, 100))
    fig.set_facecolor('black')
    ax.set_axis_off()

    # Add roads to plot
    roads = osm.get_network(network_type="driving")
    roads.plot(ax=ax, color='white')

    # Add buildings to plot
    buildings = osm.get_buildings()
    buildings.plot(ax=ax, color='gold')

    # Add county boundary to plot
    boundary = geopandas.read_file(f'{geoJson_path}/county/{county_id}.geojson')
    boundary.plot(ax=ax, facecolor='none', edgecolor='red', linewidth=5, alpha=0.5)


    plt.savefig(f'{img_path}/{county_id}_buildings_plot.png')

def GenImgAddressAnalyse():
    print("Running Address Analyses...")

    address_in_building = []
    address_out_building = []
    address_filter = {'addr:housenumber': True}
    
    boundaries = geopandas.read_file(village_geoJson_path)
    village_boundaries = boundaries[boundaries['COUNTYID'] == county_id]

    for village_boundary in village_boundaries.iterfeatures():
        village_id = village_boundary['properties']['VILLCODE']

        osm_v = pyrosm.OSM(f"./pbf/village/{village_id}.pbf")

        addresses_t = osm_v.get_data_by_custom_criteria( # Aquire all address points 
                    custom_filter=address_filter,
                    keep_nodes=True,
                    keep_ways=False,
                    keep_relations=False
                    )
        
        buildings_v = osm_v.get_buildings() # Aquire all buildings

        if addresses_t is not None:
            for address in addresses_t.iterfeatures():
                address_p = Point(address['geometry']['coordinates'][0], address['geometry']['coordinates'][1])
                if buildings_v.contains(address_p).any(): # Detect whether address is inside a building
                    address_in_building.append(address_p)
                else:
                    address_out_building.append(address_p) 

    # plot graph

    fig, ax = plt.subplots(1, 1, figsize=(100, 100))
    fig.set_facecolor('black')
    ax.set_axis_off()

    village_boundaries.plot(ax=ax, facecolor='none', edgecolor='black', alpha=0.5, zorder=100) # Plot village boudaries on top

    osm = pyrosm.OSM(f"./pbf/county/{county_id}.pbf")
    roads = osm.get_network(network_type="driving")
    roads.plot(ax=ax, color='gray')

    geopandas.GeoSeries(address_in_building).plot(ax=ax, color='green', markersize=0.5) # Plot address within a building
    geopandas.GeoSeries(address_out_building).plot(ax=ax, color='red', markersize=0.5) # Plot address without a building

    print(len(address_in_building), ' + ', len(address_out_building), ' = ', len(address_in_building)+len(address_out_building))

    plt.savefig(f'{img_path}/{county_id}_addresses_plot.png')



def GenImgAddressAnalyseWithBuilding():
    print("Running Detail Address Analyses...")

    address_filter = {'addr:housenumber': True}
    
    boundaries = geopandas.read_file(village_geoJson_path)
    village_boundaries = boundaries[boundaries['COUNTYID'] == county_id]

    fig, ax = plt.subplots(1, 1, figsize=(100, 100))
    fig.set_facecolor('black')
    ax.set_axis_off()

    norm = plt.Normalize(0, 50)

    for village_boundary in village_boundaries.iterfeatures():
        village_id = village_boundary['properties']['VILLCODE']
        print(village_boundary['properties']['VILLNAME'])

        osm_v = pyrosm.OSM(f"./pbf/village/{village_id}.pbf")

        addresses_t = osm_v.get_data_by_custom_criteria( # Aquire all address points 
                    custom_filter=address_filter,
                    keep_nodes=True,
                    keep_ways=False,
                    keep_relations=False
                    )
        
        buildings_v = osm_v.get_buildings() # Aquire all buildings
        buildings_v['count'] = 0 

        if addresses_t is not None:
            for address in addresses_t.iterfeatures():
                address_p = Point(address['geometry']['coordinates'][0], address['geometry']['coordinates'][1])
                index_in_building = buildings_v.index[buildings_v.contains(address_p)].tolist()
                for index in index_in_building: # Detect whether address is inside a building
                    buildings_v['count'][index] += 1
                    break

        colors = plt.cm.viridis(norm(buildings_v['count']))
        buildings_v.plot(ax=ax, color=colors)
        
        for i in range(len(buildings_v)):
            building_p = buildings_v['geometry'][i]
            centroid = building_p.centroid
            ax.annotate(str(buildings_v['count'][i]), xy=(centroid.x, centroid.y), color='white', fontsize=5, ha='center', zorder=200)

        # geopandas.GeoSeries(address_in_building).plot(ax=ax, color='green', markersize=0.5) # Plot address within a building
        # geopandas.GeoSeries(address_out_building).plot(ax=ax, color='red', markersize=0.5) # Plot address without a building


    village_boundaries.plot(ax=ax, facecolor='none', edgecolor='white', alpha=0.5, zorder=100) # Plot village boudaries on top

    osm = pyrosm.OSM(f"./pbf/county/{county_id}.pbf")
    roads = osm.get_network(network_type="driving")
    roads.plot(ax=ax, color='gray')

    plt.savefig(f'{img_path}/{county_id}_detail_addr_plot.png')


## Run code plotting code

# GenImgBuildingPlot()
# GenImgAddressAnalyse()
GenImgAddressAnalyseWithBuilding()













