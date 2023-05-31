import numpy
from shapely import wkt
from skimage.transform import rescale, rotate


class RescaleImage:
    def __init__(self, rescale_factor):
        self.rescale_factor = rescale_factor
    
    def apply_transformation_to_band(self, band):
        image_rescale = rescale(band, self.rescale_factor, preserve_range=True, order=0, anti_aliasing=False)
        return image_rescale
    
    def apply_transformation_to_geocoordinates(self, row_index, col_index):
        new_row_index = int(row_index*self.rescale_factor)
        new_col_index = int(col_index*self.rescale_factor)
        return new_row_index, new_col_index


class RotateImage:
    def __init__(self, rotate_angle, image_shape):
        self.rotate_angle = rotate_angle
        self.image_shape = image_shape
        self.center_col = image_shape[1] / 2 -0.5 
        self.center_row = image_shape[0] / 2 -0.5 
    
    def apply_transformation_to_band(self, band):
        image_rotate = rotate(
            band, 
            self.rotate_angle, 
            preserve_range=True, 
            order=0, 
            center=(self.center_col, self.center_row)
        )
        return image_rotate
    
    def apply_transformation_to_geocoordinates(self, row_index, col_index):
        angle_rad = numpy.deg2rad(self.rotate_angle)
        cos_theta = numpy.cos(angle_rad)
        sin_theta = numpy.sin(angle_rad)
        transform_matrix = numpy.array([[cos_theta, -sin_theta], [sin_theta, cos_theta]])
        translated_col = col_index - self.center_col
        translated_row = row_index - self.center_row
        transformed_point = numpy.dot(transform_matrix, [translated_row, translated_col])
        transformed_col = transformed_point[1] + self.center_col
        transformed_row = transformed_point[0] + self.center_row
        return transformed_row, transformed_col


class PolygoneBoundariesImage:
    def __init__(self, wkt_polygone, get_row_col_index_from_longitide_latitude):
        self.wkt_polygone = wkt_polygone
        self.get_row_col_index_from_longitide_latitude = get_row_col_index_from_longitide_latitude
        self._calculate_row_col_boundaries()
    
    def _calculate_row_col_boundaries(self):
        polygone_boudary = numpy.dstack(wkt.loads(self.wkt_polygone).boundary.xy)[0]
        row_col_list = []
        for lon, lat in polygone_boudary:
            row_col_list.append(
                self.get_row_col_index_from_longitide_latitude(lon, lat)
            )
        row_col_list = numpy.array(row_col_list)
        min_row = int(numpy.array(row_col_list)[:, 0].min())
        max_row = int(numpy.array(row_col_list)[:, 0].max())
        min_col = int(numpy.array(row_col_list)[:, 1].min())
        max_col = int(numpy.array(row_col_list)[:, 1].max())
        self._min_row = min_row
        self._max_row = max_row
        self._min_col = min_col
        self._max_col = max_col
    
    def apply_transformation_to_band(self, band):
        subset_band = band[
            self._min_row:self._max_row,
            self._min_col:self._max_col
        ]
        return subset_band

    def apply_transformation_to_geocoordinates(self, row_index, col_index):
        new_row_index = row_index - self._min_row
        new_col_index = col_index - self._min_col
        return new_row_index, new_col_index


class IdentityPolygoneBoundariesImage:
    def apply_transformation_to_band(self, band):
        return band

    def apply_transformation_to_geocoordinates(self, row_index, col_index):
        return row_index, col_index
