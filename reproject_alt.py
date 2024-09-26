import geopandas as gpd

def reproject_crs(input_file, target_epsg=32651):
    # try:
        # Read the shapefile
        gdf = gpd.read_file(input_file)
        gdf = gdf.to_crs(epsg=target_epsg)
        
        return gdf

# gdf = reproject_crs(r"C:\Users\user-307E123400\OneDrive - Philippine Space Agency\FMR\Delineations & Centerlines\undissolved\BSG-113-20240823-004447-268994436.shp")
# gdf.to_file(r"C:\Users\user-307E123400\OneDrive - Philippine Space Agency\FMR\Delineations & Centerlines\undissolved\4326.shp")
    # except FileNotFoundError:
    #     print("Error: Input file not found.")
    # except ValueError as e:
    #     print(f"Value Error: {e}")
    # except Exception as e:
    #     print(f"Error: {e}")