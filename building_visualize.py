import subprocess 
import os
import warnings
import zipfile
import geopandas 
import pandas as pd
import json
import pyrosm
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import multiprocessing

## Setting

county_id = 'X' 
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

county_geoJson_path = './geojsons/county_boundaries.geojson'
download_files = [
    {'path': county_geoJson_path, 'url': 'https://data.depositar.io/en/dataset/5fae1054-c9d5-409b-96ab-e2bd4da20960/resource/ac875414-84aa-4d89-916c-3e4e01a4d141/download/county_boundaries_remove_islands.geojson'},
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

town_shp_path = './shp/town_boundaries' # Extract town boundaries
village_shp_path = './shp/village_boundaries' # Extract village boundaries

MakeSureDirExist(town_shp_path)
MakeSureDirExist(village_shp_path)

if not os.path.exists(f'{town_shp_path}/TOWN_MOI_1140318.shp'):
    with zipfile.ZipFile('./shp/town_boundaries.zip', 'r') as zip_ref:
        zip_ref.extractall(town_shp_path)

if not os.path.exists(f'{village_shp_path}/VILLAGE_NLSC_1140620.shp'):
    with zipfile.ZipFile('./shp/village_boundaries.zip', 'r') as zip_ref: 
        zip_ref.extractall(village_shp_path)


## geoJson Data Processing

town_geoJson_path = './geojsons/town_boundaries.geojson'
village_geoJson_path = './geojsons/village_boundaries.geojson'


for file in os.listdir(town_shp_path):
    if file.endswith('.shp') and file.startswith('TOWN_MOI'):
        town_shapefile = os.path.join(town_shp_path, file)
        break

for file in os.listdir(village_shp_path):
    if file.endswith('.shp') and file.startswith('VILLAGE'):
        village_shapefile = os.path.join(village_shp_path, file)
        break


if not os.path.exists(f'{geoJson_path}/town_boundaries.geojson'): # convert shape to geojson
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



def csv_handler(data):
    csv_path = './out/data/analysis_building&addr.csv'
    if 'county_id' in data:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path) 

            if (df['county_id'] == county_id).any():
                for key, value in data.items():
                    df.loc[df['county_id'] == county_id, key] = value
            else:
                df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
        else:
            df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
    else:
        print("Error: Didn't not specify county_id in csv_handler's data ")
        return



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

def _process_single_village(village_boundary_feature, addressRadius_flag):
    village_id = village_boundary_feature['properties']['VILLCODE']
    village_name = village_boundary_feature['properties']['VILLNAME']
    print(f"{village_name} - {village_id}")

    osm_v = pyrosm.OSM(f"./pbf/village/{village_id}.pbf")
    
    local_address_in_building = []
    local_address_out_building = []

    try:
        addresses_t = osm_v.get_data_by_custom_criteria(
                            custom_filter={'addr:housenumber': True},
                            keep_nodes=True,
                            keep_ways=False,
                            keep_relations=False
                            )
        
        buildings_v = osm_v.get_buildings().set_crs(epsg=4326)

        if addresses_t is not None and buildings_v is not None:
            for address in addresses_t.iterfeatures():
                address_p = Point(address['geometry']['coordinates'][0], address['geometry']['coordinates'][1])
                if addressRadius_flag:
                    buildings_m = buildings_v.to_crs(3826)
                    address_m = geopandas.GeoSeries([address_p], crs=buildings_v.crs).to_crs(3826)
                    buffer = address_m.buffer(2).iloc[0]
                    if buildings_m.intersects(buffer).any():
                        local_address_in_building.append(address_p)
                    else:
                        local_address_out_building.append(address_p)
                else:
                    if buildings_v.intersects(address_p).any():
                        local_address_in_building.append(address_p)
                    else:
                        local_address_out_building.append(address_p)
    except Exception as e:
        print(f"Error processing {village_name} ({village_id}): {e}")
    
    return local_address_in_building, local_address_out_building

def GenImgAddressAnalyse(saveCSV=False, showBuildingFootprint=False, addressRadius=False):
    print("Running Address Analyses...")
    
    if showBuildingFootprint:
        fig, ax = plt.subplots(1, 1, figsize=(160, 160))
    else:
        fig, ax = plt.subplots(1, 1, figsize=(100, 100))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0) # make margin smaller
    fig.set_facecolor('black')
    ax.set_axis_off()

    
    boundaries = geopandas.read_file(village_geoJson_path)
    village_boundaries = boundaries[boundaries['COUNTYID'] == county_id]

    address_in_building = []
    address_out_building = []

    # Use multiprocessing to speed up the loop
    with multiprocessing.Pool(processes=os.cpu_count()) as pool:
        results = pool.starmap(_process_single_village, [(v, addressRadius) for v in village_boundaries.iterfeatures()])

    for in_b, out_b in results:
        address_in_building.extend(in_b)
        address_out_building.extend(out_b)

    # plot graph
    osm_c = pyrosm.OSM(f"./pbf/county/{county_id}.pbf")
    buildings_c = osm_c.get_buildings() 

    if showBuildingFootprint: # Plot building footprint
        buildings_c.plot(ax=ax, facecolor='none', edgecolor='gold', linewidth=0.5)

    # village_boundaries.plot(ax=ax, facecolor='none', edgecolor='black', alpha=0.5, zorder=100) # Plot village boudaries on top
    boundary = geopandas.read_file(f'{geoJson_path}/county/{county_id}.geojson')
    boundary.plot(ax=ax, facecolor='none', edgecolor='red', linewidth=5, alpha=0.5)

    osm = pyrosm.OSM(f"./pbf/county/{county_id}.pbf")
    roads = osm.get_network(network_type="driving")
    roads.plot(ax=ax, color='gray')

    geopandas.GeoSeries(address_in_building).plot(ax=ax, color='green', markersize=0.5) # Plot address within a building
    geopandas.GeoSeries(address_out_building).plot(ax=ax, color='red', markersize=0.5) # Plot address without a building

    print(len(address_in_building), ' + ', len(address_out_building), ' = ', len(address_in_building)+len(address_out_building))

    if showBuildingFootprint:
        plt.savefig(f'{img_path}/{county_id}_addresses&building_plot.png')
    else:
        plt.savefig(f'{img_path}/{county_id}_addresses_plot.png')

    if saveCSV:
        csv_handler({
            'county_id': [county_id],
            'addr_in_building': [len(address_in_building)],
            'addr_out_building': [len(address_out_building)]
        })



def GenImgAddressAnalyseWithBuilding(saveCSV=False):
    print("Running Detail Address Analyses...")

    address_filter = {'addr:housenumber': True}
    
    boundaries = geopandas.read_file(village_geoJson_path)
    village_boundaries = boundaries[boundaries['COUNTYID'] == county_id]

    fig, ax = plt.subplots(1, 1, figsize=(100, 100))
    fig.set_facecolor('black')
    ax.set_axis_off()

    norm = plt.Normalize(0, 50)

    village_total_count = len(village_boundaries)
    buildings_total_count = 0
    addr_total_count = 0
    addr_detail_count = [0, 0, 0, 0, 0, 0, 0] # 0, 1, 2~5, 6~10, 10~20, 20~50, >50
    for village_index, village_boundary in enumerate(village_boundaries.iterfeatures()):
        village_id = village_boundary['properties']['VILLCODE']
        print(f"({village_index+1}/{village_total_count})", village_boundary['properties']['VILLNAME'])

        osm_v = pyrosm.OSM(f"./pbf/village/{village_id}.pbf")

        try: 

            addresses_t = osm_v.get_data_by_custom_criteria( # Aquire all address points 
                        custom_filter=address_filter,
                        keep_nodes=True,
                        keep_ways=False,
                        keep_relations=False
                        )
            
            buildings_v = osm_v.get_buildings() # Aquire all buildings

            if addresses_t is not None and buildings_v is not None:
                buildings_total_count += len(buildings_v)
                addr_total_count += len(addresses_t)
                buildings_v['addr_count'] = 0 

                for address in addresses_t.iterfeatures():
                    address_p = Point(address['geometry']['coordinates'][0], address['geometry']['coordinates'][1])
                    index_in_building = buildings_v.index[buildings_v.contains(address_p)].tolist()
                    for index in index_in_building: # Detect whether address is inside a building
                        buildings_v['addr_count'][index] += 1
                        break

                colors = plt.cm.viridis(norm(buildings_v['addr_count']))
                buildings_v.plot(ax=ax, color=colors)

        
                ## analysis calcualtion
                if saveCSV == True:
                    for i in range(len(buildings_v)):
                        curr_addr_count = buildings_v['addr_count'][i]
                        if curr_addr_count == 0:   addr_detail_count[0] += 1
                        elif curr_addr_count == 1: addr_detail_count[1] += 1
                        elif curr_addr_count <= 5: addr_detail_count[2] += 1
                        elif curr_addr_count <= 10:addr_detail_count[3] += 1 
                        elif curr_addr_count <= 20:addr_detail_count[4] += 1
                        elif curr_addr_count <= 50:addr_detail_count[5] += 1 
                        else: addr_detail_count[6] += 1

        except Exception as e:
                print(e)



            # ax.text(s=str(buildings_v['count'][i]), x=centroid.x, y=centroid.y, color='gray', fontsize=5, ha='center', zorder=200)



    # village_boundaries.plot(ax=ax, facecolor='none', edgecolor='white', alpha=0.5, zorder=100) # Plot village boudaries on top
    boundary = geopandas.read_file(f'{geoJson_path}/county/{county_id}.geojson')
    boundary.plot(ax=ax, facecolor='none', edgecolor='red', linewidth=5, alpha=0.5)

    osm = pyrosm.OSM(f"./pbf/county/{county_id}.pbf")
    roads = osm.get_network(network_type="driving")
    roads.plot(ax=ax, color='gray')

    plt.savefig(f'{img_path}/{county_id}_detail_addr_plot.png')

    if saveCSV == True:
        csv_handler({
            'county_id': [county_id],
            'building_count': [buildings_total_count],
            'address_count': [addr_total_count],
            '0': [addr_detail_count[0]],
            '1': [addr_detail_count[1]],
            '2~5': [addr_detail_count[2]],
            '6~10': [addr_detail_count[3]],
            '10~20': [addr_detail_count[4]],
            '20~50': [addr_detail_count[5]],
            '>50': [addr_detail_count[6]]
        })








## Run code plotting code

# GenImgBuildingPlot()
GenImgAddressAnalyse(saveCSV=False, showBuildingFootprint=True, addressRadius=True)
# GenImgAddressAnalyseWithBuilding(saveCSV=True)
