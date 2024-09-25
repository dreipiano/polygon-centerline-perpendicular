import geopandas as gpd
from pyproj import CRS

def reproject_crs(input_file, target_epsg=32651):
    try:
        # Read the shapefile
        gdf = gpd.read_file(input_file)

        # Get the current CRS
        current_crs = gdf.crs
        
        # Check if the input CRS is defined
        if current_crs is None:
            raise ValueError("The shapefile does not have a CRS defined.")
        
        print(f"Current CRS: {current_crs}")
        
        # Define target CRS
        target_crs = CRS.from_epsg(target_epsg)

        # Check if reprojection is necessary
        if current_crs.to_epsg() == target_epsg:
            print("The shapefile is already in the {current_crs}. No reprojection needed.")
        else:
            print("Reprojecting to target CRS...")
            # Reproject to target CRS
            gdf = gdf.to_crs(epsg=target_epsg)
            print("Reprojection successful!")
        
        return gdf

    except FileNotFoundError:
        print("Error: Input file not found.")
    except ValueError as e:
        print(f"Value Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
