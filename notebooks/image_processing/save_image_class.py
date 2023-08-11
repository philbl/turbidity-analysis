from pathlib import Path
from tqdm import tqdm
from datetime import datetime

from src.satellite_image_processing.image_handler.general_image_handler import (
    BouctoucheImageHandler,
    CocagneImageHandler
)


if __name__ == "__main__":
    sat_folder_list = list(filter(lambda path: ".zip" in str(path), list(Path("data/sentinel2_data/bouctouche").iterdir())))
    for sat_zip in tqdm(sat_folder_list):
        date = datetime.strptime(sat_zip.name.split("_")[2].split("T")[0], "%Y%m%d")
        date_string = date.strftime("%Y-%m-%d")

        if Path(f"data/cocagne_class/cocagne_{date_string}.pkl").exists() is False:
            cocagne_image_handler = CocagneImageHandler(sat_zip)
            cocagne_image_handler.save("data/cocagne_class")
            del cocagne_image_handler

        if Path(f"data/bouctouche_class/bouctouche_{date_string}.pkl").exists() is False:
            bouctouche_image_handler = BouctoucheImageHandler(sat_zip)
            bouctouche_image_handler.save("data/bouctouche_class")
            del bouctouche_image_handler
