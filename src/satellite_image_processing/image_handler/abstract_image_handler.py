from abc import ABC, abstractmethod
import rasterio
import numpy
import pickle
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
from skimage.transform import rescale

from src.satellite_image_processing.projections import (
    project_epsg4326_to_epsg_32620
)

class AbstractImageHandler(ABC):
    BAND_NAME_MAPPING = {
        "blue_band": "B02",
        "green_band": "B03",
        "red_band": "B04",
        "nir_band": "B08",
        "cloud_prob": "MSK_CLDPRB_20m"
    }
    def __init__(self, zip_path):
        self.zip_path = zip_path
        loaded_data_dict = self._get_data_from_zip_file(self.zip_path)
        self._image_shape = loaded_data_dict["blue_band"].shape # TODO Clean that
        self._date = loaded_data_dict["date"]
        self._cloud_coverage = loaded_data_dict["cloud_coverage"]
        self._crs = loaded_data_dict["crs"]
        self._affine_matrix = loaded_data_dict["affine_matrix"]
        #self._index_function = loaded_data_dict["index_function"]
        transformed_data_dict = self._apply_image_transformation_list(loaded_data_dict)
        self._subset_transformed_data_dict = self._apply_image_wkt_polygone_subset(transformed_data_dict)
    
    @property
    @abstractmethod
    def estuary_name(self):
        """Name of the Estuary"""

    @property
    def blue_band(self):
        return self._subset_transformed_data_dict["blue_band"]
    
    @property
    def green_band(self):
        return self._subset_transformed_data_dict["green_band"]
    
    @property
    def red_band(self):
        return self._subset_transformed_data_dict["red_band"]
    
    @property
    def nir_band(self):
        return self._subset_transformed_data_dict["nir_band"]
    
    @property
    def cloud_prob(self):
        return self._subset_transformed_data_dict["cloud_prob"]
    
    @property
    def cloud_coverage(self):
        return self._cloud_coverage
    
    @property
    def calculated_cloud_coverage(self):
        return (self._subset_transformed_data_dict["cloud_prob"] > 25).mean()
    
    @property
    def date(self):
        return self._date
    
    @property
    def crs(self):
        return self._crs
    
    @property
    def affine_matrix(self):
        return self._affine_matrix
    
    @property
    def index_function(self):
        return self._index_function
    
    @property
    def image_shape(self):
        return self._image_shape
    
    def index_function(self, longitude, latitude):
        # Invert the affine transformation
        inv_affine = ~self.affine_matrix

        # Transform the x, y input coordinates
        transformed_coords = inv_affine * (longitude, latitude)

        # Round the transformed coordinates to the nearest integer indices
        row_index = int(transformed_coords[1])
        col_index = int(transformed_coords[0])

        # Return the transformed indices
        return row_index, col_index
    
    @abstractmethod
    def _image_transformation_list(self):
        """
        List of image transformation to apply
        """
    
    @abstractmethod
    def _image_wkt_polygone_subset(self):
        """
        wkt representation of the polygone subset
        """

    def _apply_image_transformation_list(self, loaded_data_dict):
        transformed_data_dict = {}
        for band_name in self.BAND_NAME_MAPPING.keys():
            band = loaded_data_dict[band_name].copy()
            for transformation in self._image_transformation_list():
                band = transformation.apply_transformation_to_band(band)
            transformed_data_dict[band_name] = band
        return transformed_data_dict
    
    def _get_row_col_index_after_transformation_from_longitide_latitude(self, longitude, latitude):
        projected_longitude, projected_latitute = project_epsg4326_to_epsg_32620(longitude, latitude)
        row_index, col_index = self.index_function(projected_longitude, projected_latitute)
        for transformation in self._image_transformation_list():
            row_index, col_index = transformation.apply_transformation_to_geocoordinates(row_index, col_index)
        return row_index, col_index
    
    def _apply_image_wkt_polygone_subset(self, transformed_data_dict):
        polygone_subset_data_dict = {}
        for band_name in self.BAND_NAME_MAPPING.keys():
            band = transformed_data_dict[band_name].copy()
            subset_band = self._image_wkt_polygone_subset().apply_transformation_to_band(band)
            polygone_subset_data_dict[band_name] = subset_band
        return polygone_subset_data_dict
    
    def get_row_col_index_from_longitide_latitude(self, longitude, latitude):
        row_index, col_index = self._get_row_col_index_after_transformation_from_longitide_latitude(longitude, latitude)
        row_index, col_index = self._image_wkt_polygone_subset().apply_transformation_to_geocoordinates(row_index, col_index)
        return row_index, col_index

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
        with zipfile.ZipFile(Path(zip_path), "r") as f:
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
            file_list = granule_file if band_name == "cloud_prob" else R10m_file
            path = list(filter(lambda file: band_code in file.filename, file_list))[0].filename
            band = rasterio.open(Path(zip_format_path, path), driver="JP2OpenJPEG").read(1)
            data_dict[band_name] = band
            if band_name == "blue_band":
                with rasterio.open(Path(zip_format_path, path), driver="JP2OpenJPEG") as src:
                    #index_function = src.index
                    crs = src.crs
                    affine_matrix = src.transform
        # msk_cldprb_20m_path = list(filter(lambda file: "MSK_CLDPRB_20m" in file.filename, granule_file))[0].filename
        # data_dict["MSK_CLASSI_B00"] = rasterio.open(Path(zip_format_path, msk_classi_b00_path), driver="JP2OpenJPEG").read(1)
        # data_dict["MSK_CLDPRB_20m"] = rasterio.open(Path(zip_format_path, msk_cldprb_20m_path), driver="JP2OpenJPEG").read(1)
        # with rasterio.open(Path(zip_format_path, path), driver="JP2OpenJPEG") as src:
        #     index_function = src.index
        #     crs = src.crs
        #data_dict["index_function"] = index_function
        data_dict["crs"] = str(crs)
        data_dict["affine_matrix"] = affine_matrix

        data_dict["cloud_prob"] = rescale(data_dict["cloud_prob"], 2, preserve_range=True, order=0)

        return data_dict

    def save(self, saving_folder):
        saving_name = f"{self.estuary_name}_{self.date.split('T')[0]}.pkl"
        with open(Path(saving_folder, saving_name), "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, file_path):
        with open(file_path, "rb") as f:
            obj = pickle.load(f)
        return obj
