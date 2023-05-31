import rasterio
import numpy
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET


def get_data_from_zip_file(zip_path):
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

    granule_file = list(filter(lambda file: "GRANULE" in file.filename, all_file_name))
    R10m_file = list(filter(lambda file: "R10m" in file.filename, granule_file))
    blue_band_path = list(filter(lambda file: "B02" in file.filename, R10m_file))[0].filename
    green_band_path = list(filter(lambda file: "B03" in file.filename, R10m_file))[0].filename
    red_band_path = list(filter(lambda file: "B04" in file.filename, R10m_file))[0].filename
    nir_band_path = list(filter(lambda file: "B08" in file.filename, R10m_file))[0].filename

    blue_band = rasterio.open(Path(zip_format_path, blue_band_path), driver="JP2OpenJPEG").read(1)
    green_band = rasterio.open(Path(zip_format_path, green_band_path), driver="JP2OpenJPEG").read(1)
    red_band = rasterio.open(Path(zip_format_path, red_band_path), driver="JP2OpenJPEG").read(1)
    nir_band = rasterio.open(Path(zip_format_path, nir_band_path), driver="JP2OpenJPEG").read(1)

    with rasterio.open(Path(zip_format_path, blue_band_path), driver="JP2OpenJPEG") as src:
        index_function = src.index
        source = src
    
    return {
        "date": date,
        "cloud_coverage": cloud_coverage,
        "blue_band": blue_band,
        "green_band": green_band,
        "red_band": red_band,
        "nir_band": nir_band,
        "index_function": index_function,
        "source": source
    }


def apply_gamma_to_band(band, gamma):
    band_gamma = band**(1/gamma)
    max_value = band_gamma.max()
    min_value = band_gamma.min()
    x_max_min_gap = max_value - min_value
    band_gamma_normalized = (band_gamma-min_value)/x_max_min_gap
    return band_gamma_normalized


def apply_beta_to_band(band, beta):
    band_beta = band*(1/beta)
    max_value = band_beta.max()
    min_value = band_beta.min()
    x_max_min_gap = max_value - min_value
    band_beta_normalized = (band_beta-min_value)/x_max_min_gap
    return band_beta_normalized


def get_rgb_image_from_data_dict(data_dict, beta=3000):
    band2_blue = data_dict["blue_band"]
    band3_green = data_dict["green_band"]
    band4_red = data_dict["red_band"]

    blue_float = numpy.clip(band2_blue/beta, 0, 1)
    green_float = numpy.clip(band3_green/beta, 0, 1)
    red_float = numpy.clip(band4_red/beta, 0, 1)

    rgb = numpy.dstack((red_float, green_float, blue_float))
    return rgb
