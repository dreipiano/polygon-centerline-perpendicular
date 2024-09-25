import geopandas as gpd
import os

# Set the path to your folder containing shapefiles
input_folder = ("C:\\Users\\user-307E953400\\Desktop\\test")
output_folder = os.path.join(input_folder, 'dissolved_output')

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.shp'):
        # Read the shapefile
        shapefile_path = os.path.join(input_folder, filename)
        gdf = gpd.read_file(shapefile_path)
        
        # Dissolve all features into one
        dissolved_gdf = gdf.dissolve()

        # Save the dissolved shapefile
        output_path = os.path.join(output_folder, filename)
        dissolved_gdf.to_file(output_path)

print("Dissolving completed. Output saved in:", output_folder)