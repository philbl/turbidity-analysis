from src.satellite_data.polygon_subset.polygon_subset import PolygonSubset
from src.satellite_data.polygon_folder_manager.polygon_folder_manager import PolygonFolderManager


GREAT_AREA_NAME = "ipe_morell"

if __name__ == "__main__":
    polygon_folder_manager = PolygonFolderManager(GREAT_AREA_NAME)
    polygon_subset = PolygonSubset(polygon_folder_manager)
    polygon_subset.apply_polygon_subset_from_source_path_to_destination_list()
    polygon_folder_manager.delete_zip_file_in_source_path_that_are_in_destination_list()
