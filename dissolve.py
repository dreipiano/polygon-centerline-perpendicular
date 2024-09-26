import geopandas as gpd

# Loop through all files in the input folder
def dissolve(input_file):
    
    # Dissolve all features into one
    gdf = input_file.dissolve()
    return gdf
