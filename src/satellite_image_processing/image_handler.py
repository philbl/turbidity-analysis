import rasterio
import numpy
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

from src.satellite_image_processing.image_transformation import (
    RescaleImage
)

class ImageHandler:
    BAND_NAME_MAPPING = {
        "blue_band": "B02",
        "green_band": "B03",
        "red_band": "B04",
        "nir_band": "B08"
    }
    def __init__(self, zip_path):
        self.zip_path = zip_path
        loaded_data_dict = self._get_data_from_zip_file(self.zip_path)
        self._date = loaded_data_dict["date"]
        self._cloud_coverage = loaded_data_dict["cloud_coverage"]
        self._crs = loaded_data_dict["crs"]
        self._tranformed_data_dict = self._apply_transform(loaded_data_dict)
    
    @property
    def blue_band(self):
        return self._tranformed_data_dict["blue_band"]
    
    @property
    def green_band(self):
        return self._tranformed_data_dict["green_band"]
    
    @property
    def red_band(self):
        return self._tranformed_data_dict["red_band"]
    
    @property
    def nir_band(self):
        return self._tranformed_data_dict["nir_band"]
    
    @property
    def cloud_coverage(self):
        return self._cloud_coverage
    
    @property
    def date(self):
        return self._date
    
    @property
    def crs(self):
        return self._crs
    
    def _transform_list(self):
        transform_list = [
            RescaleImage(0.1)
        ]
        return transform_list

    def _apply_transform(self, loaded_data_dict):
        transformed_data_dict = {}
        for band_name in self.BAND_NAME_MAPPING.keys():
            band = loaded_data_dict[band_name].copy()
            for transformation in self._transform_list():
                band = transformation.apply_transformation_to_band(band)
            transformed_data_dict[band_name] = band
        return transformed_data_dict
    
    def get_row_col_index_from_longitide_latitude(self, longitude, latitude):
        pass

    def get_rgb_float_true_color_image(self, beta=3000):
        blue_float = numpy.clip(self.blue_band/beta, 0, 1)
        green_float = numpy.clip(self.green_band/beta, 0, 1)
        red_float = numpy.clip(self.red_band/beta, 0, 1)

        rgb = numpy.dstack((red_float, green_float, blue_float))
        return rgb

    def _get_data_from_zip_file(self, zip_path):
        zip_path = str(Path(zip_path))
        zip_format_path = f"zip+file:{zip_path}!"
        meta_data_path = str(Path(zip_path.split("\\")[-1].replace("zip", "SAFE"), "MTD_MSIL2A.xml")).replace("\\", "/")
        with zipfile.ZipFile(zip_path, "r") as f:
            meta_data = ET.fromstring(str(f.read(meta_data_path), "UTF-8"))
            all_file_name = f.filelist
        general_info = meta_data.find("{https://psd-14.sentinel2.eo.esa.int/PSD/User_Product_Level-2A.xsd}General_Info")
        product_info = general_info.find("Product_Info")
        date = product_info.find("PRODUCT_START_TIME").text

        quality_ind = meta_data.find("{https://psd-14.sentinel2.eo.esa.int/PSD/User_Product_Level-2A.xsd}Quality_Indicators_Info")
        cloud_coverage = float(quality_ind.find("Cloud_Coverage_Assessment").text)

        data_dict = {
            "date": date,
            "cloud_coverage": cloud_coverage
        }

        granule_file = list(filter(lambda file: "GRANULE" in file.filename, all_file_name))
        R10m_file = list(filter(lambda file: "R10m" in file.filename, granule_file))
        for band_name, band_code in self.BAND_NAME_MAPPING.items():
            path = list(filter(lambda file: band_code in file.filename, R10m_file))[0].filename
            band = rasterio.open(Path(zip_format_path, path), driver="JP2OpenJPEG").read(1)
            data_dict[band_name] = band
        with rasterio.open(Path(zip_format_path, path), driver="JP2OpenJPEG") as src:
            index_function = src.index
            crs = src.crs
        data_dict["index_function"] = index_function
        data_dict["crs"] = str(crs)

        return data_dict
