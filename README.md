# Taiwan Building Footprint

![logo image](taiwan-building-footprint/logo.webp)

#### CONTENTS 
- [OSM Address and Building Analysis](#osm-address-and-building-analysis) 
- [Tiles Generation](#tiles-generation)
- [Building Segmentaiton](#building-segmentation)

## OSM Address and Building Analysis 

#### FILES
- Code - `building_visualize.py`
- Jupyter Book - `taiwan-building-footprint/`

#### RESULT
- [Analysis/visualize on Jupyter book](https://liquidcs.github.io/Taiwan-Buildings-Footprint/intro.html)
- [Raw Data without Visualization](https://github.com/liquidCS/Taiwan-Buildings-Footprint/blob/main/out/data/analysis_building%26addr.csv)

#### DEPENDENCY 
- [Osmium](https://osmcode.org/osmium-tool/index.html)
    - [Installation Guide](https://osmcode.org/osmium-tool/manual.html#installation)
- Python Library 
    - [pandas](https://pypi.org/project/pandas/), [geopandas](https://pypi.org/project/geopandas/), [pyrosm](https://pypi.org/project/pyrosm/)
    - [matplotlib](https://pypi.org/project/matplotlib/)
    - zipfile

#### RUN
> [!NOTE]
> On first execution, approximately 300 MB of OSM data will be downloaded.

```
sudo apt install osmium-tool
pip install -r requirements.txt
python building_visualize.py [county_id] 
```

#### OPTIONS
> [!IMPORTANT]
> Options like --addressAnalysis with --radius and --detailAddressAnalysis can take up 15 minutes to run.
```
usage: building_visualize.py [-h] [--buildingWithRoad] [--addressAnalysis] [--radius] [--showFootprint] [--detailAddressAnalysis] [--saveCSV] county_id

positional arguments:
  county_id             The county ID you want to generate.

options:
  -h, --help            show this help message and exit
  --buildingWithRoad    Generate image with buildings and roads
  --addressAnalysis     Generate image of address where green means address loacation is in building and red is outside the building.
  --radius              Analysis address with a margin of 2m of error when consider whether it is in a building.
  --showFootprint       Show building outline when generating address analysis.
  --detailAddressAnalysis
                        Generate image of building with different colors representing how many address a building has.
  --saveCSV             Store analysis result to out/data/analysis_building&addr.csv
```


## Tiles Generation

#### FILES 
- Code - `tiles/data.py`
- Output - `tiles/data/train_images`, `tiles/data/train_masks` 

#### DEPENDENCY 
- [pyrosm](https://pypi.org/project/pyrosm/), [geopandas](https://pypi.org/project/pandas/)
- [matplotlib](https://pypi.org/project/matplotlib/), [contextily](https://contextily.readthedocs.io/en/latest/intro_guide.html)

#### RUN
```
cd tiles/
pip install -r requirements.txt
python data.py [x] [y] [z]
```

#### OPTIONS
```
usage: data.py [-h] x y z

Generate binary map using OSM buildings data.

positional arguments:
  x           x - WMP horizontal tile index
  y           y - WMP vertical tile index
  z           z - WMP zoom level
```

## Building Segmentation




