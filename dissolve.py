import geopandas as gpd

# Loop through all files in the input folder
def dissolve(input_file):
    gdf = gpd.read_file(input_file)
            
    # Dissolve all features into one
    gdf = gdf.dissolve()
    return gdf