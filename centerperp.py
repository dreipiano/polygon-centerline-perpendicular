import geopandas as gpd
import pygeoops
from shapely.geometry import LineString, MultiLineString
import numpy as np

#Create polygon centerline 
def create_centerline(gdf_polygon, dense = 0.1, tole = 0.001):
    """Creates the centerline of the polygon."""
    gdf_lines = pygeoops.centerline(gdf_polygon.geometry, densify_distance=dense, simplifytolerance=tole)
    gdf_lines = gpd.GeoDataFrame(geometry=gdf_lines, crs=gdf_polygon.crs)
    
    return gdf_lines

#Create perpendicular lines
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


#Prints the widths of the perpendicular lines
def print_width(gdf):
    """Print details of each line in the GeoDataFrame."""
    for idx, row in gdf.iterrows():
        geom = row.geometry
        print(f"Length: {geom.length:.3f} meters")

#Removes perpendicular lines that intersect with other lines
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

#≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
#≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈

# Main Execution
# if __name__ == "__main__":
#     # Load the polygon shapefile
#     gdf_polygons = gpd.read_file(r"C:\Users\user-307E123400\Documents\DIGITAL AGRI\FMR\Reprojected\dissolved_BSG-113-20240823-004447-268994436-Tiff.shp")

#     # Creates and saves the centerline of the polygon
#     centerline = create_centerline(gdf_polygons)

#     # Create perpendicular lines
#     perp_lines = create_perp(gdf_polygons, centerline)

#     # Remove intersecting perpendicular lines
#     perp_gdf = remove_intersect(perp_lines)

#     # Print the details of the filtered perpendicular lines
#     print_width(perp_gdf)

#     centerline.to_file(r"C:\Users\user-307E123400\Documents\DIGITAL AGRI\FMR\Reprojected\cltest-dissolved_BSG-113-20240823-004447-268994436-Tiff.shp")
#     perp_gdf.to_file(r"C:\Users\user-307E123400\Documents\DIGITAL AGRI\FMR\Reprojected\perptest-dissolved_BSG-113-20240823-004447-268994436-Tiff.shp")
