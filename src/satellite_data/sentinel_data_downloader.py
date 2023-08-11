from sentinelsat import SentinelAPI
from sentinelsat.exceptions import InvalidChecksumError
from dataclasses import asdict
from datetime import datetime
import numpy
import time
from pathlib import Path

from src.satellite_data.models.sentinel_api_query_input import SentinelAPIQueryInput
from src.satellite_data.polygon_folder_manager.polygon_folder_manager import PolygonFolderManager


class SentinelDataDownloader:
    _URL = "https://apihub.copernicus.eu/apihub"

    def __init__(
        self,
        username: str,
        password: str,
        sentinel_api_query_input: SentinelAPIQueryInput,
        polygon_folder_manager: PolygonFolderManager
    ):
        self.api = SentinelAPI(
            username, password, self._URL
        )
        self.polygon_folder_manager = polygon_folder_manager
        self.download_directory_path = Path(self.polygon_folder_manager.source_path)
        self.sentinel_api_query_input = sentinel_api_query_input
        self.products_df = self._get_products_df()

    def _get_products_df(self):
        products = self.api.query(**asdict(self.sentinel_api_query_input))
        products_df = self.api.to_dataframe(products)
        return products_df

    def _determine_if_folder_zip_is_already_downloaded(self, folder_name):
        is_file_in_source_path = Path(self.download_directory_path, f"{folder_name}.zip").is_file()

        is_file_in_all_destination_path = all(
            [
                Path(destination_dict["destination_path"], f"{folder_name}.zip").is_file() for 
                    destination_dict in self.polygon_folder_manager.destination_list
            ]
        )
        return is_file_in_source_path or is_file_in_all_destination_path

    def _get_not_downloaded_uuid_isonline_dict(self):
        uuid_dict = {}
        for _, row in self.products_df.iterrows():
            uuid = row["uuid"]
            folder_name = row["title"]
            if self._determine_if_folder_zip_is_already_downloaded(folder_name) is False:
                uuid_dict[uuid] = self.api.is_online(uuid)
        print(f"Number of uuid: {len(self.products_df)}")
        print(f"Number of uuid to download: {len(uuid_dict)}")
        print(f"Number of online uuid: {numpy.array(list(uuid_dict.values())).sum()}")
        self.uuid_dict = uuid_dict

    def trigger_download_of_offline_uuid(self, sleeping_time=1920):
        self._get_not_downloaded_uuid_isonline_dict()
        number_of_trigger = 0
        for uuid, is_online in self.uuid_dict.items():
            if is_online is False:
                number_of_trigger += 1
                try:
                    self.api.download(
                        id=uuid, directory_path=str(self.download_directory_path)
                    )
                except Exception as e:
                    print(f"{number_of_trigger}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {e}")
                    time.sleep(sleeping_time)

    def download_online_uuid(self):
        self._get_not_downloaded_uuid_isonline_dict()
        number_of_download = 0
        number_to_download = numpy.array(list(self.uuid_dict.values())).sum()
        for uuid, is_online in self.uuid_dict.items():
            if is_online:
                number_of_download += 1
                print(f"{number_of_download}/{number_to_download}")
                try:
                    self.api.download(
                        id=uuid, directory_path=str(self.download_directory_path)
                    )
                except InvalidChecksumError:
                    print(f"InvalidChecksumError {uuid}")
