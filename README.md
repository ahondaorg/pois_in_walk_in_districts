##POIs in walk in district
Generate geojson file of POIs and street network with in walking distance from ditrict center

**What this code do?**
1. make district street graph(sub_g) from Whole area street network in each district
2. make walking route graph within sub_g
3. filter pois in radius in district walking graph
4. save geojson

**Required python packages**
shapley		github.com/shapely/shapely
geopandas	github.com/geopandas/geopandas
netwworks	github.com/networkx/networkx
osmnx		github.com/gboeing/osmnx

**Scrennshot of data visualization**
Data visualization on QGIS
![screenshot](screenshot/poi_in_district.png)
