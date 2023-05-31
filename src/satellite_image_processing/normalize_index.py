def create_ndwi_raster(green_band, nir_band):
    green_band = green_band.astype(float)
    nir_band = nir_band.astype(float)
    ndwi = (green_band - nir_band)/(green_band + nir_band)
    return ndwi


def create_ndti_raster(red_band, green_band):
    red_band = red_band.astype(float)
    green_band = green_band.astype(float)
    ndti = (red_band - green_band)/(red_band + green_band)
    return ndti
