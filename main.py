import geopandas as gpd
import os
import center_perp as cp
import reproject

def check_file_type(file_path):
    """Check if the file is a valid GeoPackage or Shapefile."""
    valid_extensions = ['.gpkg', '.shp']
    _, ext = os.path.splitext(file_path)
    return ext.lower() in valid_extensions

def main():
    # Get user input for file path
    input_file = input("Enter the path to the GeoDataFrame file (GeoPackage or Shapefile): ")

    # Check if the file type is valid
    if not check_file_type(input_file):
        print("Error: The file must be a GeoPackage (.gpkg) or a Shapefile (.shp).")
        return

    # Load the GeoDataFrame
    try:
        gdf_poly = gpd.read_file(input_file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    #Dissolve
    
    
    # Check the CRS of the GeoDataFrame
    gdf_poly = reproject.reproject_crs(input_file)
    

    #Smoothing/Simplify
    
    # Print details of the original lines
    print("Original line details:")
    cp.print_width(gdf_poly)

    # Create perpendicular lines
    perpendicular_lines = cp.create_perp(gdf_poly)

    # Create a GeoDataFrame for the new lines
    gdf_perpendicular = gpd.GeoDataFrame(geometry=perpendicular_lines, crs=gdf_poly.crs)

    # Remove intersecting lines
    gdf_non_intersecting = cp.remove_intersect(gdf_perpendicular)

    # Print details of the remaining lines
    print("Details of non-intersecting perpendicular lines:")
    cp.print_width(gdf_non_intersecting)

    # Save the non-intersecting lines to a new file
    output_file = input("Enter the path to save the non-intersecting lines (e.g., output.shp): ")
    try:
        gdf_non_intersecting.to_file(output_file)
        print(f"Non-intersecting lines saved to: {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    main()
