import geopandas as gpd
import pygeoops
from shapely.geometry import LineString, MultiLineString
import numpy as np

def dissolve(gdf):
    """
    From geopandas.GeoDataFrame
    For reference: https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.dissolve.html
    
    This method is used to merge geometries in a GeoDataFrame based on a specified attribute. 
    This function combines adjacent features that share the same value for the designated attribute into a 
    single geometry, effectively simplifying the dataset.
    
    Parameters
    ------
    gdf (geometry, GeoSeries or arraylike): A polygon or multipolygon
        
   Raises
   ------
   ValueError
       DESCRIPTION.

   Returns
   ------- 
   gdf (geometry, GeoSeries or arraylike)
        
    """
    return gdf.dissolve()

def reproject(gdf, target_epsg=32651):
    """
    From geopandas.GeoDataFrame. 
    This method is used to transform the coordinate reference system (CRS) of a GeoDataFrame to a specified CRS. 
    By providing a new CRS, through specifying EPSG code, this method reprojects the geometries in the GeoDataFrame 
    accordingly.

    Parameters
    ----------
    gdf (geometry, GeoSeries or arraylike): A polygon or multipolygon

    epsg (int) : EPSG code specifying output projection.The default is 32651.
    
    Raises
    ------
    ValueError
        DESCRIPTION.

    Returns
    ------- 
    gdf (geometry, GeoSeries or arraylike)

    """
    return gdf.to_crs(epsg=target_epsg)

def smoothen(gdf, buffer_distance=5, simplify_tolerance=1, resolution=40):
    """
    From geopandas GeoSeries.
    This algorithm first creates a buffer area around all features in the input layer using a specified distance. 
    It then simplifies the resulting geometries, producing a new layer with fewer vertices while preserving the 
    overall shape, utilizing methods such as the Douglas-Peucker or Visvalingam algorithms. This process effectively 
    smooths and reduces the complexity of the original geometries.
        
    Parameters
    ----------
    gdf (geometry, GeoSeries or arraylike): A polygon or multipolygon
    
    buffer_distance (float): radius of the buffer in the Minkowski sum (or difference)
    simplify_tolerance (float): All parts of a simplified geometry will be no more than tolerance distance from the 
        original. It has the same units as the coordinate reference system of the GeoSeries. For example, 
        using tolerance=100 in a projected CRS with meters as units means a distance of 100 meters in reality.
    resolution (int): The resolution of the buffer around each vertex. Specifies the number of linear segments in 
        a quarter circle in the approximation of circular arcs.
        
        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        ------- 
        gdf (geometry, GeoSeries or arraylike)
    """
    if gdf.empty:
        return gdf
    smoothed_gdf = gdf
    smoothed_gdf['geometry'] = smoothed_gdf.geometry.apply(lambda geom: 
        geom.buffer(buffer_distance, resolution=resolution)
        .buffer(-buffer_distance, resolution=resolution)
        .simplify(simplify_tolerance, preserve_topology=True))
    return smoothed_gdf

def create_centerline(gdf, dense = 0.1, tole = 0.01):
    """
    From pygeoops. Calculates an approximated centerline/s for a polygon/multipolygon. Negative values for the algorithm parameters will result in an automatic optimisation based on the average geometry width for each input geometry.

    Parameters
    ----------
    gdf (geometry, GeoSeries or arraylike): A polygon or multipolygon
    
    dense (float): Densify input geometry so each segment has maximum this length. 
                    A reasonable value is the typical minimal width of the input geometries. 
                    If a larger value is used centerlines might have holes on narrow places in the input geometry. 
                    The smaller the value choosen, the longer the processing will take.
                    The default is 0.1.
    tole (float): Tolerance to simplify the resulting centerline (using Douglas-Peucker algoritm). 
                    The default is 0.01.

    Raises
    ------
    ValueError
        DESCRIPTION.

    Returns
    -------
    (GeoDataFrame): The centerline for each of the input geometries.

    """
    gdf_lines = pygeoops.centerline(gdf.geometry, densify_distance=dense, simplifytolerance=tole)
    gdf_lines = gpd.GeoDataFrame(geometry=gdf_lines, crs=gdf.crs)
    
    return gdf_lines

def create_perp(gdf_polygon, gdf_lines, distance=10, interval=5):
    """
    Calculates and creates perpendicular lines at certain intervals along a centerline within the polygon.

    Parameters
    ----------
    gdf_polygon (geometry, GeoSeries or arraylike): A polygon or multipolygon
    gdf_lines (geometry, GeoSeries or arraylike): A line or multiline
    
    distance(int) : Refers to the length of a perpendicular line extended in one direction from a central point. 
        The default distance is 10.
    interval (int): Refers to the interval per perpendicular lines. The higher the value, the lesser number of 
        perpendicular lines. The default is 5.

    Raises
    ------
    ValueError
        DESCRIPTION.

    Returns
    -------
    new_perp (geometry, GeoSeries or arraylike): Returns a multiline of lines perpendicular to the edges of the polygon.

    """
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

def remove_intersect(gdf):
    """
    The function takes a GeoDataFrame (`gdf`) containing a line or multiline and removes any lines that intersect 
    with others. It iterates through each line and checks for intersections with all other lines in the GeoDataFrame. 
    If a line does not intersect with any others, it is added to a list of non-intersecting lines. Finally, the 
    function returns a new GeoDataFrame containing only the non-intersecting lines, preserving the original 
    coordinate reference system (CRS).

    
    Parameters
    ----------
    gdf (geometry, GeoSeries or arraylike): A geometry that is a line or multiline
        DESCRIPTION.

    Raises
    ------
    ValueError
        DESCRIPTION.

    Returns
    -------
    non_intersecting_lines (geometry, GeoSeries or arraylike)

    """
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

def print_width(gdf):
    """
    Print details of each widtrh in the GeoDataFrame.

    Parameters
    ----------
    gdf (geometry, GeoSeries or arraylike): A geometry, GeoSeries or arraylike.

    Raises
    ------
    ValueError
        DESCRIPTION.

    Returns
    -------
    None.

    """
    for idx, row in gdf.iterrows():
        geom = row.geometry
        print(f"Length: {geom.length:.3f} meters")
