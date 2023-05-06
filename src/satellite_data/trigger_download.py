from datetime import date

from src.satellite_data.sentinel_data_downloader import SentinelDataDownloader
from src.satellite_data.models.sentinel_api_query_input import SentinelAPIQueryInput

USER = None
PASSWORD = None


if __name__ == "__main__":
    sentinel_api_query_input = SentinelAPIQueryInput(
        area = "POLYGON ((-64.68 46.54, -64.90 46.44, -64.8549047 46.3459426, -64.57 46.46, -64.68 46.54))",
        date=(date(2022, 5, 1), date(2022, 10, 1)),
        #date=(date(2023, 5, 1), date(2023, 10, 1)),
        platformname='Sentinel-2',
        processinglevel = 'Level-2A',
        cloudcoverpercentage=(0, 100)
    )

    sentinel_data_downloader = SentinelDataDownloader(
        USER,
        PASSWORD,
        "data/sentinel2_data/bouctouche",
        sentinel_api_query_input
    )

    sentinel_data_downloader.trigger_download_of_offline_uuid()
