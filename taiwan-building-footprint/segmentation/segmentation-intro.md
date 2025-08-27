# Intro 

## Building Segmentation

#### DEPENDENCY
Segment Anything Model (Meta)
    - [Direct Download Link](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth)
Python Library: 
    - segment_anything, opencv
    - matplotlib, numpy 

#### RUN

``` {note}
Must download Segment-Anything model form meta before running.
```

```
cd segmentation/
pip install -r requirements.txt
python predict_all.py x y z
```

#### OPTIONS
```
usage: predict_all.py [-h] x y z

Generate building boundaries prediction using satellite tiles.

positional arguments:
  x           x - WMP horizontal tile index
  y           y - WMP vertical tile index
  z           z - WMP zoom level

options:
  -h, --help  show this help message and exit
```
