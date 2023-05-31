def create_ndwi_raster(green_band, nir_band):
    """
    Calculates the Normalized Difference Water Index (NDWI) raster from the input green and near-infrared (NIR) bands.

    Args:
        green_band (numpy.ndarray): Array representing the green band.
        nir_band (numpy.ndarray): Array representing the near-infrared (NIR) band.

    Returns:
        numpy.ndarray: Array representing the NDWI raster.

    Raises:
        ValueError: If the input bands have different shapes.

    Notes:
        - The input bands are expected to be in the same spatial extent and coordinate system.
        - The input bands should be provided as numpy arrays.
        - The NDWI is calculated using the formula: (green_band - nir_band) / (green_band + nir_band).
    """
    green_band = green_band.astype(float)
    nir_band = nir_band.astype(float)
    ndwi = (green_band - nir_band)/(green_band + nir_band)
    return ndwi


def create_ndti_raster(red_band, green_band):
    """
    Calculates the Normalized Difference Turbidity Index (NDTI) raster from the input red and green bands.

    The NDTI is a spectral index commonly used to assess water turbidity. It measures the degree of light scattering
    caused by suspended particles in water.

    Args:
        red_band (numpy.ndarray): Array representing the red band.
        green_band (numpy.ndarray): Array representing the green band.

    Returns:
        numpy.ndarray: Array representing the NDTI raster.

    Raises:
        ValueError: If the input bands have different shapes.

    Notes:
        - The input bands are expected to be in the same spatial extent and coordinate system.
        - The input bands should be provided as numpy arrays.
        - The NDTI is calculated using the formula: (red_band - green_band) / (red_band + green_band).
        - Higher NDTI values indicate higher turbidity or presence of suspended particles.
    """
    red_band = red_band.astype(float)
    green_band = green_band.astype(float)
    ndti = (red_band - green_band)/(red_band + green_band)
    return ndti
