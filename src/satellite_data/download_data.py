from datetime import date

from src.satellite_data.sentinel_data_downloader import SentinelDataDownloader
from src.satellite_data.models.sentinel_api_query_input import SentinelAPIQueryInput
from src.satellite_data.config import area_dict

USER = None
PASSWORD = None
AREA = "bouctouche"


if __name__ == "__main__":
    sentinel_api_query_input = SentinelAPIQueryInput(
        area=area_dict[AREA],
        date=(date(2022, 5, 1), date(2022, 10, 1)),
        # date=(date(2023, 5, 1), date(2023, 10, 1)),
        platformname="Sentinel-2",
        processinglevel="Level-2A",
        cloudcoverpercentage=(0, 100),
    )

    sentinel_data_downloader = SentinelDataDownloader(
        USER, PASSWORD, f"data/sentinel2_data/{AREA}", sentinel_api_query_input
    )

    sentinel_data_downloader.download_online_uuid()
