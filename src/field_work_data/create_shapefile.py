import geopandas
import fire
import numpy
import pandas
from pathlib import Path
from shapely.geometry import Point
import json


def create_sensor_location_shapefile(json_folder_path, sensor_type, output_folder):
    json_path_list = list(Path(json_folder_path).iterdir())
    assert sensor_type in ["ADCP", "turbidity_probe"]
    df = pandas.DataFrame(columns=["deployment_date", "longitude", "latitude", "estuary_name"])
    for i, json_path in enumerate(json_path_list):
        with open(json_path, "r") as f:
            field_dict = json.load(f)
        df.loc[i, "deployment_date"] = field_dict["date"]
        df.loc[i, "estuary_name"] = field_dict["estuary_name"]
        geo_coordinates = field_dict[sensor_type]["geo_coordinates"]
        df.loc[i, "longitude"] = geo_coordinates["lon"]
        df.loc[i, "latitude"] = geo_coordinates["lat"]
    
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    gdf = geopandas.GeoDataFrame(df, geometry=geometry)
    output_shapefile = Path(output_folder, f"{sensor_type}.shp")
    gdf.to_file(output_shapefile, driver='ESRI Shapefile', crs="EPSG:4326")


def create_spatial_turbidity_shapefile(json_folder_path, output_folder):
    json_path_list = list(Path(json_folder_path).iterdir())
    df = pandas.DataFrame(columns=["date","time", "notes", "depth", "median_turbidity", "longitude", "latitude", "estuary_name"])
    i = 0
    for json_path in json_path_list:
        with open(json_path, "r") as f:
            field_dict = json.load(f)
        date = field_dict["date"]
        estuary_name = field_dict["estuary_name"]
        measurements_list = field_dict["spatial_turbidity_measurement"]["measurements_list"]
        for mesaurement in measurements_list:
            df.loc[i, "date"] = date
            df.loc[i, "estuary_name"] = estuary_name
            df.loc[i, "time"] = mesaurement["time"]
            df.loc[i, "notes"] = mesaurement["notes"]
            df.loc[i, "depth"] = mesaurement["depth"]
            df.loc[i, "median_turbidity"] = numpy.median(mesaurement["measures"])
            geo_coordinates = mesaurement["geo_coordinates"]
            df.loc[i, "longitude"] = geo_coordinates["lon"]
            df.loc[i, "latitude"] = geo_coordinates["lat"]
            i += 1

    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    gdf = geopandas.GeoDataFrame(df, geometry=geometry)
    output_shapefile = Path(output_folder, "spatial_turbidity.shp")
    gdf.to_file(output_shapefile, driver='ESRI Shapefile', crs="EPSG:4326")


if __name__ == "__main__":
    fire.Fire()
