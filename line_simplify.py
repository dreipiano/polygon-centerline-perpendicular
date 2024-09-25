import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
import matplotlib.pyplot as plt

# Path to the input shapefile
input_shapefile = (".shp")

# Read the shapefile into a GeoDataFrame
try:
    gdf = gpd.read_file(input_shapefile)
except Exception as e:
    print(f"Error reading shapefile: {e}")
    raise

def smooth_geometry(geom, buffer_distance=2.5, simplify_tolerance=2):
    if geom.is_empty:
        return geom
    if isinstance(geom, (Polygon, MultiPolygon)):
        # Apply buffering and simplification to the geometry
        geom = geom.buffer(buffer_distance).buffer(-buffer_distance)
        geom = geom.simplify(simplify_tolerance, preserve_topology=True)
    return geom

# Apply the smoothing function to each geometry in the GeoDataFrame
smoothed_gdf = gdf.copy()
smoothed_gdf['geometry'] = smoothed_gdf['geometry'].apply(lambda geom: smooth_geometry(geom, buffer_distance=2.5, simplify_tolerance=2))

# Plotting the smoothed geometries with the original geometries overlaid
fig, ax = plt.subplots(figsize=(10, 10), dpi=300)

# Plot smoothed geometries
smoothed_gdf.plot(ax=ax, edgecolor='black', facecolor='lightgreen', alpha=0.5, label='Smoothed Geometry')

# Overlay original geometries
gdf.plot(ax=ax, edgecolor='red', facecolor='none', linewidth=0.5, label='Original Geometry')

# Add title and legend
ax.set_title('Original Geometry Overlaid on Smoothed Geometry')
ax.legend()
ax.set_axis_off()  # Hide the axes for a cleaner look

# Adjust layout to make sure everything fits nicely
plt.tight_layout()

# Optionally save the plot
plt.savefig('output_plot.png', dpi=300)

# Path to save the output shapefile
output_shapefile = (".shp")

# Save the smoothed GeoDataFrame to a new shapefile
try:
    smoothed_gdf.to_file(output_shapefile)
    print(f"Smoothed geometries saved to: {output_shapefile}")
except Exception as e:
    print(f"Error saving shapefile: {e}")

plt.show()
