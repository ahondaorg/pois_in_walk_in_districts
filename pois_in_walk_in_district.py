import geopandas as gpd
from shapely.geometry import LineString

import networkx as nx
import osmnx as ox


g_proj = ox.io.load_graphml("./data/YOUR_STREET.xml") ###whole street network GraphML

gdf_base = gpd.read_file('./data/YOUR_DISTRICTS.geojson') ###district area geojson 

my_pois = gpd.read_file("./data/YOUR_POIS.geojson") ### POIs geojson
my_pois = my_pois.to_crs(epsg = 25833) ### apply proper EPSG

this_gdf_base_len = len(gdf_base)
my_pois_in_districts = []


for index in range(3):#for test purpose calculate only 3 districts

    this_districts = gdf_base.loc[index]
    this_districtID = this_districts['district_ID'] # ID of each districts 
   
    print("-----",this_districtID,index,'/',this_gdf_base_len)

    
    ###make sub_g
    ### first make buffer
    ###in epsg 4326, 100m = 0.001

    point = this_districts.geometry.centroid
    bbox_buffer = this_districts.geometry.buffer(distance = 1000, join_style="mitre")
    bbox_buffer_gdf = gpd.GeoDataFrame(geometry = [bbox_buffer], crs = gdf_base.crs)

    sub_g = ox.truncate.truncate_graph_polygon(g_proj,bbox_buffer)
    ox.io.save_graphml(sub_g,"./out/poi_disticts_walk/" + this_districtID +"-sub_g_gpaph.xml")# make GraphML for further usage

    sub_g_node_gdf,sub_g_edge_gdf  = ox.convert.graph_to_gdfs(sub_g)

    sub_g_edge_gdf.to_file("./out/poi_disticts_walk/" + this_districtID +"-sub_g.geojson", driver="GeoJSON")# make geojson for further usage

    ### query POIs in walking distance in sug_g graph

    bezirk_point = this_districts.geometry.centroid

    walking_speed = 5000/3600 #meter persec
    walking_time = 10*60 #in seconds
    max_distance = walking_speed * walking_time  # in meters

    nearest_node = ox.distance.nearest_nodes(sub_g, bezirk_point.x, bezirk_point.y)

    all_nodes = sub_g.nodes()
    nodes_within_distance = []

    for node in all_nodes:
        try:
            if nx.shortest_path_length(sub_g, source=nearest_node, target=node, weight='length') <= max_distance:
                nodes_within_distance.append(node)
        except:
            pass

    edges_within_distance = [(u, v) for u, v in sub_g.edges() if u in nodes_within_distance or v in nodes_within_distance]

    edge_geometries =[]
    for u, v in edges_within_distance:
        edge_geom = LineString([(sub_g.nodes[u]['x'], sub_g.nodes[u]['y']), (sub_g.nodes[v]['x'], sub_g.nodes[v]['y'])])
        edge_geometries.append(edge_geom)

    ###need convert edges to gdf
    in_walk_edge = gpd.GeoDataFrame(geometry = edge_geometries, crs="EPSG:25833")

    in_walk_edge.to_file("./out/poi_disticts_walk/" + this_districtID + "-street_walk_route.geojson", driver="GeoJSON")

    ### extract pois in in walk distance
    poi_max_dist = 40
    filtered_gdf = gpd.sjoin_nearest(my_pois, in_walk_edge, how ='inner', max_distance=poi_max_dist, distance_col = 'poi_distance',exclusive = True)
    ###need remove duplicates..

    filtered_gdf = filtered_gdf.drop_duplicates(subset=['id'])

    filtered_gdf.to_file("./out/poi_disticts_walk/" + this_districtID + "-pois_walk_poi.geojson", driver="GeoJSON")

    ###need calculate each POIs sum
    this_pois ={}
    this_pois['district_ID'] = this_districtID
    this_pois['geometry'] = this_districts.geometry

    ####calculate poi statics
    poi_count = filtered_gdf['poi_name'].value_counts(dropna = False).to_dict()
    #print(ethno_count)
    poi_count['unknown_'] = poi_count.pop('unknown')
    #print(ethno_count)
    this_pois.update(poi_count)
    #print(this_poi_bezirk)

    my_pois_in_districts.append(this_pois)

pois_in_district_walk_gdf = gpd.GeoDataFrame(my_pois_in_districts, crs="EPSG:25833")
pois_in_district_walk_gdf.to_file("./out/poi_disticts_walk/pois_in_bezirk_walk.geojson", driver="GeoJSON")

print("--END---",now)