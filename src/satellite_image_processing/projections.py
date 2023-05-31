import pyproj


def project_epsg4326_to_epsg_32620(longitude, latitude):
    wgs84 = pyproj.CRS("EPSG:4326")
    utm32620 = pyproj.CRS("EPSG:32620")
    transformer = pyproj.Transformer.from_crs(wgs84, utm32620, always_xy=True)
    return transformer.transform(longitude, latitude)
