import geopandas as gpd
import pygeoops
from shapely.geometry import LineString, MultiLineString
import numpy as np

def dissolve(gdf):
    """
    Description
    
    Parameters:
        input_file: 
    """
    return gdf.dissolve()

def reproject(gdf, target_epsg=32651):
    return gdf.to_crs(epsg=target_epsg)

def smoothen(gdf, buffer_distance=5, simplify_tolerance=1, resolution=40):
    if gdf.empty:
        return gdf
    smoothed_gdf = gdf
    smoothed_gdf['geometry'] = smoothed_gdf.geometry.apply(lambda geom: 
        geom.buffer(buffer_distance, resolution=resolution)
        .buffer(-buffer_distance, resolution=resolution)
        .simplify(simplify_tolerance, preserve_topology=True))
    return smoothed_gdf

def create_centerline(gdf, dense = 0.1, tole = 0.01):
    """Creates the centerline of the polygon."""
    gdf_lines = pygeoops.centerline(gdf.geometry, densify_distance=dense, simplifytolerance=tole)
    gdf_lines = gpd.GeoDataFrame(geometry=gdf_lines, crs=gdf.crs)
    
    return gdf_lines

def create_perp(gdf_polygon, gdf_lines, distance=10, interval=5):
    """Create a series of perpendicular lines at specified intervals from each line feature in a GeoDataFrame."""
    new_perp = []

    for idx, row in gdf_lines.iterrows():
        geom = row.geometry
        
        if isinstance(geom, LineString):
            length = geom.length
            num_lines = int(length // interval) + 1  # Calculate number of perpendicular lines based on interval

            for i in range(num_lines):
                position = i * interval
                point = geom.interpolate(position)

                # Find the next point along the line to determine the direction
                next_position = min(position + interval, length)
                next_point = geom.interpolate(next_position)
                direction = np.array(next_point.coords[0]) - np.array(point.coords[0])
                angle = np.arctan2(direction[1], direction[0])
                perp_angle = angle + np.pi / 2

                # Create the perpendicular line
                perp_start = np.array(point.coords[0]) + distance * np.array([np.cos(perp_angle), np.sin(perp_angle)])
                perp_end = np.array(point.coords[0]) - distance * np.array([np.cos(perp_angle), np.sin(perp_angle)])

                perpendicular_line = LineString([tuple(perp_start), tuple(perp_end)])
                new_perp.append(perpendicular_line)

        elif isinstance(geom, MultiLineString):
            for line in geom.geoms:
                length = line.length
                num_lines = int(length // interval) + 1  # Calculate number of perpendicular lines based on interval

                for i in range(num_lines):
                    position = i * interval
                    point = line.interpolate(position)

                    next_position = min(position + interval, length)
                    next_point = line.interpolate(next_position)
                    direction = np.array(next_point.coords[0]) - np.array(point.coords[0])
                    angle = np.arctan2(direction[1], direction[0])
                    perp_angle = angle + np.pi / 2

                    # Create the perpendicular line
                    perp_start = np.array(point.coords[0]) + distance * np.array([np.cos(perp_angle), np.sin(perp_angle)])
                    perp_end = np.array(point.coords[0]) - distance * np.array([np.cos(perp_angle), np.sin(perp_angle)])

                    perpendicular_line = LineString([tuple(perp_start), tuple(perp_end)])
                    new_perp.append(perpendicular_line)
        else:
            raise ValueError("Unsupported geometry type")
    new_perp = gpd.GeoDataFrame(geometry=new_perp, crs=gdf_polygon.crs)
    new_perp = gpd.overlay(new_perp, gdf_polygon, how='intersection')    
    new_perp['id'] = range(len(new_perp))
    new_perp['width'] = new_perp.geometry.length
    
    return new_perp

def remove_intersect(gdf):
    """Remove intersecting lines from the GeoDataFrame."""
    non_intersecting_lines = []
    
    for i, geom1 in enumerate(gdf.geometry):
        intersects = False
        for j, geom2 in enumerate(gdf.geometry):
            if i != j and geom1.intersects(geom2):
                intersects = True
                break
        if not intersects:
            non_intersecting_lines.append(geom1)
    
    return gpd.GeoDataFrame(geometry=non_intersecting_lines, crs=gdf.crs)

def print_width(gdf):
    """Print details of each line in the GeoDataFrame."""
    for idx, row in gdf.iterrows():
        geom = row.geometry
        print(f"Length: {geom.length:.3f} meters")
