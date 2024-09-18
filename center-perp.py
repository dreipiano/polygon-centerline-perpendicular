"""
≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
NOTE

Ang kulang na lang ay yung pagkuha ng road width ranges per interval.
≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
"""

import geopandas as gpd
import pygeoops
from shapely.geometry import LineString, MultiLineString
import numpy as np

#Create perpendicular lines
def create_perpendicular_lines(gdf_lines, distance=10, interval=20):
    """Create a series of perpendicular lines at specified intervals from each line feature in a GeoDataFrame."""
    new_geometries = []

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
                new_geometries.append(perpendicular_line)

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
                    new_geometries.append(perpendicular_line)
        else:
            raise ValueError("Unsupported geometry type")

    return new_geometries


#Prints the widths of the perpendicular lines
def print_line_details(gdf):
    """Print details of each line in the GeoDataFrame."""
    for idx, row in gdf.iterrows():
        geom = row.geometry
        print(f"Length: {geom.length:.3f} meters")

#Removes perpendicular lines that intersect with other lines
def remove_intersecting_lines(gdf):
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

#≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
#≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈

# Main Execution
if __name__ == "__main__":
    # Load the polygon shapefile
    gdf_polygons = gpd.read_file(r"C:\Users\user-307E123400\OneDrive - Philippine Space Agency\FMR\Delineations & Centerlines\Transformed\For test (simplified)\smoothed_BSG-115-20240601-230805-244346461.shp")

    # Creates and saves the centerline of the polygon
    gdf_lines = pygeoops.centerline(gdf_polygons.geometry, densify_distance=0.1, simplifytolerance=0.01)
    gdf_lines = gpd.GeoDataFrame(geometry=gdf_lines, crs=gdf_polygons.crs)
#    gdf_lines.to_file(r"C:\Users\user-307E123400\OneDrive - Philippine Space Agency\FMR\Delineations & Centerlines\Transformed\For test (simplified)\cl-smoothed_BSG-115-20240601-230805-244346461.shp")

    # Create perpendicular lines
    perp_lines = create_perpendicular_lines(gdf_lines)

    # Create a GeoDataFrame for perpendicular lines
    perp_gdf = gpd.GeoDataFrame(geometry=perp_lines, crs=gdf_polygons.crs)

    # Trim perpendicular lines by polygon
    perp_gdf = gpd.overlay(perp_gdf, gdf_polygons, how='intersection')

    # Remove intersecting perpendicular lines
    perp_gdf = remove_intersecting_lines(perp_gdf)

    # Print the details of the filtered perpendicular lines
    print("Road widths per perpendicular line")
    print()
    print_line_details(perp_gdf)

    perp_gdf['id'] = range(len(perp_gdf))
    perp_gdf['width'] = perp_gdf.geometry.length
    perp_gdf.to_file(r"C:\Users\user-307E123400\OneDrive - Philippine Space Agency\FMR\Delineations & Centerlines\Transformed\For test (simplified)\perp-smoothed_BSG-115-20240601-230805-244346461.shp")
