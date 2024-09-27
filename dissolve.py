import geopandas as gpd    # Used only for debugging

# Loop through all files in the input folder
def dissolve(input_file):
    
    # Dissolve all features into one
    gdf = input_file.dissolve()
    return gdf

# gdf = gpd.read_file("")
# gdf = dissolve_poly(gdf)
# gdf.to_file("")
