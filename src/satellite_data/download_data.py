from datetime import date
import getpass

from src.satellite_data.sentinel_data_downloader import SentinelDataDownloader
from src.satellite_data.models.sentinel_api_query_input import SentinelAPIQueryInput
from src.satellite_data.polygon_folder_manager.polygon_folder_manager import PolygonFolderManager
from src.satellite_data.polygon_subset.polygon_subset import PolygonSubset


USER = "phil190"
PASSWORD = getpass.getpass()
GREAT_AREA_LIST = ["nb_bouctouche_cocagne", "ipe_dunk_west", "ipe_morell"] # Choice are ["nb_bouctouche_cocagne", "ipe_dunk_west", "ipe_morell"]
YEAR_LIST = [2022, 2023]


if __name__ == "__main__":
    for great_area in GREAT_AREA_LIST:
        for year in YEAR_LIST:
            print(f"Downloading {great_area} {year}")
            polygon_folder_manager = PolygonFolderManager(great_area)
            sentinel_api_query_input = SentinelAPIQueryInput(
                area=polygon_folder_manager.download_polygon,
                date=(date(year, 5, 1), date(year, 11, 1)),
                platformname="Sentinel-2",
                processinglevel="Level-2A",
                cloudcoverpercentage=(0, 100),
            )

            sentinel_data_downloader = SentinelDataDownloader(
                USER, PASSWORD, sentinel_api_query_input, polygon_folder_manager
            )

            sentinel_data_downloader.download_online_uuid()
            
            polygon_subset = PolygonSubset(polygon_folder_manager)
            polygon_subset.apply_polygon_subset_from_source_path_to_destination_list()
            polygon_folder_manager.delete_zip_file_in_source_path_that_are_in_destination_list()
