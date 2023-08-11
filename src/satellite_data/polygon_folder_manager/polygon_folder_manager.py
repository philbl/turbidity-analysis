from pathlib import Path

from src.satellite_data.polygon_folder_manager.estuaries_polygon import (
    GREAT_AREA_POLYGON_DICT
)
from src.satellite_data.polygon_folder_manager.folder_management import FOLDER_MANAGEMENT


class PolygonFolderManager:
    """
    Class to handle the folder management when downloading data via Sentinel2 API. 
    When downloading Sentinel2 data, a polygon is used to make the query, then the image downloaded
    contains that polygon but also a way bigger image. So for two differents polygon, it
    might return the same big images. 
    This class handle to retrieve where the original data will be downloaded (source path) and where it will
    be saved when it's gonna be split by the src.satellite_data.polygon_subset.polygon_subset.PolygonSubset
    It also handle how to delete the file in the source path when it has been split in the destination list.
    """
    def __init__(self, great_area_name):
        self.great_area_name = great_area_name
        self._source_path = self._get_source_path()
        self._destination_list = self._get_destination_list()
        self._download_polygon = self._get_download_polygon()

    def _validate_greate_area_name(self, great_area_name):
        assert great_area_name in [
            "nb_bouctouche_cocagne",
            "ipe_dunk_west",
            "ipe_morell"
        ]

    @property
    def source_path(self):
        return self._source_path

    @property
    def destination_list(self):
        return self._destination_list

    @property
    def download_polygon(self):
        return self._download_polygon

    def _get_source_path(self):
        return FOLDER_MANAGEMENT[self.great_area_name]["source_path"]

    def _get_destination_list(self):
        destination_list = FOLDER_MANAGEMENT[self.great_area_name]["destination_list"]
        for destination in destination_list:
            destination_name = destination["estuary_name"]
            destination["polygon"] = GREAT_AREA_POLYGON_DICT[destination_name]
        return destination_list

    def _get_download_polygon(self):
        polygon = self.destination_list[0]["polygon"]
        return polygon

    def delete_zip_file_in_source_path_that_are_in_destination_list(self):
        """
        Delete the zip file in the source path, if the file is now present in all the 
        destination path list
        """
        file_list = [file for file in Path(self.source_path).iterdir()]
        for file in file_list:
            filename = file.name
            if all(
                [
                    Path(destination_dict["destination_path"], filename).is_file() for 
                        destination_dict in self.destination_list
                ]
            ):
                file.unlink()
