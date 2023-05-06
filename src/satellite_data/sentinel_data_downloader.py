from sentinelsat import SentinelAPI
from dataclasses import asdict
from datetime import datetime
import numpy
import time
from pathlib import Path

from src.satellite_data.models.sentinel_api_query_input import SentinelAPIQueryInput


class SentinelDataDownloader:
    _URL = "https://apihub.copernicus.eu/apihub"

    def __init__(
        self,
        username: str,
        password: str,
        download_directory_path: str,
        sentinel_api_query_input: SentinelAPIQueryInput,
    ):
        self.api = SentinelAPI(
            username, password, "https://apihub.copernicus.eu/apihub"
        )
        self.download_directory_path = Path(download_directory_path)
        self.sentinel_api_query_input = sentinel_api_query_input
        self.products_df = self._get_products_df()

    def _get_products_df(self):
        products = self.api.query(**asdict(self.sentinel_api_query_input))
        products_df = self.api.to_dataframe(products)
        return products_df

    def _get_not_downloaded_uuid_isonline_dict(self):
        uuid_dict = {}
        for _, row in self.products_df.iterrows():
            uuid = row["uuid"]
            folder_name = row["title"]
            if (
                Path(self.download_directory_path, f"{folder_name}.zip").is_file()
                is False
            ):
                uuid_dict[uuid] = self.api.is_online(uuid)
        print(f"Number of uuid: {len(self.products_df)}")
        print(f"Number of uuid to download: {len(uuid_dict)}")
        print(f"Number of online uuid: {numpy.array(list(uuid_dict.values())).sum()}")
        self.uuid_dict = uuid_dict

    def trigger_download_of_offline_uuid(self, sleeping_time=1920):
        self._get_not_downloaded_uuid_isonline_dict()
        for uuid, is_online in self.uuid_dict.items():
            if is_online is False:
                try:
                    self.api.download(
                        id=uuid, directory_path=str(self.download_directory_path)
                    )
                except Exception as e:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {e}")
                    time.sleep(sleeping_time)

    def download_online_uuid(self):
        self._get_not_downloaded_uuid_isonline_dict()
        for _, row in self.products_df.iterrows():
            uuid = row["uuid"]
            if self.uuid_dict.get(uuid, False) is True:
                self.api.download(
                    id=uuid, directory_path=str(self.download_directory_path)
                )
