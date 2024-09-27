"""
≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈

NOTE

This Python script is designed to generate center and perpendicular lines from existing polygon geometries within a GeoDataFrame. 
Using libraries like shapely, numpy, geopandas, and pygeoops, it calculates the lengths of these lines and facilitates the analysis 
of geometric relationships in spatial data. The script first loads a polygon shapefile and creates centerlines from it, then generates 
a series of perpendicular lines at specified intervals. The generated center and perpendicular lines are saved separately as shapefiles 
for easy access and further use in GIS applications.


≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
"""

import geopandas as gpd
import os
import centerperp as cp
import reproject
import dissolve
import line_simplify

def main():
    # Get user input for file path
    input_file = input("Enter the path to the GeoDataFrame file (GeoPackage or Shapefile): ")

    # # Check if the file type is valid
    # if not check_file_type(input_file):
    #     print("Error: The file must be a GeoPackage (.gpkg) or a Shapefile (.shp).")
    #     return

    # Load the GeoDataFrame
    # try:
    gdf_poly = gpd.read_file(input_file)
    # except Exception as e:
    #     print(f"Error loading file: {e}")
    #     return

    #Dissolve
    dissolved_poly = dissolve.dissolve_poly(gdf_poly)
    
    # Reproject
    reprojected_poly = reproject.reproject_crs(dissolved_poly)
    
    #Smoothing/Simplify
    simplify_poly = line_simplify.smoothen(reprojected_poly)
    
    #Centerline
    centerline = cp.create_centerline(simplify_poly)

    # Perpendicular lines
    perp_lines = cp.create_perp(simplify_poly, centerline)

    # Remove intersecting lines
    # gdf_non_intersecting = cp.remove_intersect(perpendicular_lines)

    # Print width
    cp.print_width(perp_lines)

    # Save simplified poly, centerline, and perpendicular lines
    output_file = input("Enter the path to save the simplified polygon, its centerline, and perpendicular lines: ")
    simplify_poly.to_file(os.path.join(output_file, "Simplified Polygon.shp"))
    centerline.to_file(os.path.join(output_file, "centerline.shp"))
    perp_lines.to_file(os.path.join(output_file, "perp.shp"))
    # gdf_non_intersecting.to_file(os.path.join(output_file, "perpendicular.shp"))
    
    # try:
    #     gdf_non_intersecting.to_file(output_file)
    #     print(f"Non-intersecting lines saved to: {output_file}")
    # except Exception as e:
    #     print(f"Error saving file: {e}")

if __name__ == "__main__":
    main()
