import rasterio
import numpy
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

from src.satellite_image_processing.image_handler.abstract_image_handler import (
    AbstractImageHandler
)
from src.satellite_image_processing.polygon import PRECISE_POLYGON_DICT
from src.satellite_image_processing.image_transformation import (
    RescaleImage,
    RotateImage,
    PolygoneBoundariesImage,
    IdentityPolygoneBoundariesImage
)

class GeneralImageHandler(AbstractImageHandler):
    @property
    def estuary_name(self):
        return "general"
    
    def _image_transformation_list(self):
        transform_list = [
            #RescaleImage(0.1)
        ]
        return transform_list
    
    def _image_wkt_polygone_subset(self):
        return IdentityPolygoneBoundariesImage()


class BouctoucheImageHandler(AbstractImageHandler):
    @property
    def estuary_name(self):
        return "bouctouche"
    
    def _image_transformation_list(self):
        transform_list = [
            RotateImage(-45, self.image_shape)
        ]
        return transform_list
    
    def _image_wkt_polygone_subset(self):
        return PolygoneBoundariesImage(
            PRECISE_POLYGON_DICT["bouctouche"],
            self._get_row_col_index_after_transformation_from_longitide_latitude
        )


class CocagneImageHandler(AbstractImageHandler):
    @property
    def estuary_name(self):
        return "cocagne"
    
    def _image_transformation_list(self):
        transform_list = []
        return transform_list
    
    def _image_wkt_polygone_subset(self):
        return PolygoneBoundariesImage(
            PRECISE_POLYGON_DICT["cocagne"],
            self._get_row_col_index_after_transformation_from_longitide_latitude
        )


class WestImageHandler(AbstractImageHandler):
    @property
    def estuary_name(self):
        return "west"
    
    def _image_transformation_list(self):
        transform_list = []
        return transform_list
    
    def _image_wkt_polygone_subset(self):
        return PolygoneBoundariesImage(
            PRECISE_POLYGON_DICT["west"],
            self._get_row_col_index_after_transformation_from_longitide_latitude
        )


class MorellImageHandler(AbstractImageHandler):
    @property
    def estuary_name(self):
        return "morell"
    
    def _image_transformation_list(self):
        transform_list = []
        return transform_list
    
    def _image_wkt_polygone_subset(self):
        return PolygoneBoundariesImage(
            PRECISE_POLYGON_DICT["morell"],
            self._get_row_col_index_after_transformation_from_longitide_latitude
        )


class DunkImageHandler(AbstractImageHandler):
    @property
    def estuary_name(self):
        return "dunk"
    
    def _image_transformation_list(self):
        transform_list = []
        return transform_list
    
    def _image_wkt_polygone_subset(self):
        return PolygoneBoundariesImage(
            PRECISE_POLYGON_DICT["dunk"],
            self._get_row_col_index_after_transformation_from_longitide_latitude
        )
