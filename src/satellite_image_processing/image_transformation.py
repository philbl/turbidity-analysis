import numpy
from shapely import wkt
from skimage.transform import rescale, rotate


class RescaleImage:
    """
    A class for rescaling images and transforming geocoordinates based on a rescale factor.

    Parameters:
        rescale_factor (float): The factor by which to rescale the image.

    Methods:
        apply_transformation_to_band(band):
            Rescales the given image band based on the rescale factor.

        apply_transformation_to_geocoordinates(row_index, col_index):
            Transforms the given row and column indices based on the rescale factor.
    """
    def __init__(self, rescale_factor):
        self.rescale_factor = rescale_factor
    
    def apply_transformation_to_band(self, band):
        """
        Rescales the given image band based on the rescale factor.

        Parameters:
            band (ndarray): The image band to be rescaled.

        Returns:
            ndarray: The rescaled image band.

        Notes:
            This method uses the skimage `rescale` function to rescale the image band
            based on the provided rescale factor. The `preserve_range` option ensures
            that the original data range is maintained, and the `order` option specifies
            the interpolation order to use (nearest-neighbor interpolation is used here).
            The rescaled band is returned as an ndarray.
        """
        image_rescale = rescale(band, self.rescale_factor, preserve_range=True, order=0, anti_aliasing=False)
        return image_rescale
    
    def apply_transformation_to_geocoordinates(self, row_index, col_index):
        """
        Transforms the given row and column indices based on the rescale factor.

        Parameters:
            row_index (int): The original row index.
            col_index (int): The original column index.

        Returns:
            tuple: A tuple containing the transformed row and column indices as integers.

        Notes:
            This method multiplies the original row and column indices by the rescale factor
            and rounds them to the nearest integer values. The transformed indices are then
            returned as a tuple.
        """
        new_row_index = int(row_index*self.rescale_factor)
        new_col_index = int(col_index*self.rescale_factor)
        return new_row_index, new_col_index


class RotateImage:
    """
    A class for rotating images based on a specified angle and image shape.

    Parameters:
        rotate_angle (float): The angle (in degrees) by which to rotate the image.
        image_shape (tuple): The shape of the image as a tuple (height, width).

    Methods:
        apply_transformation_to_band(band):
            Rotates the given image band based on the specified angle and image shape.
            Returns the rotated image band.

        apply_transformation_to_geocoordinates(row_index, col_index):
            Transforms the given row and column indices based on the rotation angle and image shape.
            Returns the transformed row and column indices.
    """
    def __init__(self, rotate_angle, image_shape):
        """
        Initialize the RotateImage object with the specified rotate angle and image shape.

        Parameters:
            rotate_angle (float): The angle (in degrees) by which to rotate the image.
            image_shape (tuple): The shape of the image as a tuple (height, width).
        """
        self.rotate_angle = rotate_angle
        self.image_shape = image_shape
        self.center_col = image_shape[1] / 2 -0.5 
        self.center_row = image_shape[0] / 2 -0.5 
    
    def apply_transformation_to_band(self, band):
        """
        Apply rotation transformation to the given image band.

        Parameters:
            band (ndarray): The image band to be rotated.

        Returns:
            ndarray: The rotated image band.
        """
        image_rotate = rotate(
            band, 
            self.rotate_angle, 
            preserve_range=True, 
            order=0, 
            center=(self.center_col, self.center_row)
        )
        return image_rotate
    
    def apply_transformation_to_geocoordinates(self, row_index, col_index):
        """
        Apply rotation transformation to the given row and column indices.

        Parameters:
            row_index (int): The original row index.
            col_index (int): The original column index.

        Returns:
            tuple: The transformed row and column indices.
        """
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
    """
    A class for defining an image subset based on the boundaries of a polygon.

    Parameters:
        wkt_polygone (str): The well-known text representation of the polygon.
        get_row_col_index_from_longitide_latitude (callable): A function that maps longitude and latitude
            coordinates to row and column indices in the image.

    Methods:
        apply_transformation_to_band(band):
            Extracts the subset of the given image band defined by the polygon boundaries.
            Returns the subset image band.

        apply_transformation_to_geocoordinates(row_index, col_index):
            Transforms the given row and column indices to match the subset image boundaries.
            Returns the transformed row and column indices.
    """
    def __init__(self, wkt_polygone, get_row_col_index_from_longitide_latitude):
        """
        Initialize the PolygoneBoundariesImage object with the specified polygon boundaries and coordinate mapping function.

        Parameters:
            wkt_polygone (str): The well-known text representation of the polygon.
            get_row_col_index_from_longitide_latitude (callable): A function that maps longitude and latitude
                coordinates to row and column indices in the image.
        """
        self.wkt_polygone = wkt_polygone
        self.get_row_col_index_from_longitide_latitude = get_row_col_index_from_longitide_latitude
        self._calculate_row_col_boundaries()
    
    def _calculate_row_col_boundaries(self):
        """
        Calculate the row and column boundaries of the polygon.

        This private method calculates the minimum and maximum row and column indices
        based on the polygon boundaries and the provided coordinate mapping function.
        """
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
        """
        Apply the transformation to the given image band.

        Extracts the subset of the image band defined by the polygon boundaries.

        Parameters:
            band (ndarray): The image band to be transformed.

        Returns:
            ndarray: The subset image band.
        """
        subset_band = band[
            self._min_row:self._max_row,
            self._min_col:self._max_col
        ]
        return subset_band

    def apply_transformation_to_geocoordinates(self, row_index, col_index):
        """
        Apply the transformation to the given row and column indices.

        Transforms the given row and column indices to match the subset image boundaries.

        Parameters:
            row_index (int): The original row index.
            col_index (int): The original column index.

        Returns:
            tuple: The transformed row and column indices.
        """
        new_row_index = row_index - self._min_row
        new_col_index = col_index - self._min_col
        return new_row_index, new_col_index


class IdentityPolygoneBoundariesImage:
    """
    A class that represents an identity transformation for image bands and geocoordinates.

    Methods:
        apply_transformation_to_band(band):
            Applies the identity transformation to the given image band.
            Returns the input image band unchanged.

        apply_transformation_to_geocoordinates(row_index, col_index):
            Applies the identity transformation to the given row and column indices.
            Returns the input row and column indices unchanged.
    """
    def apply_transformation_to_band(self, band):
        """
        Apply the identity transformation to the given image band.

        Parameters:
            band (ndarray): The image band to be transformed.

        Returns:
            ndarray: The input image band unchanged.
        """
        return band

    def apply_transformation_to_geocoordinates(self, row_index, col_index):
        """
        Apply the identity transformation to the given row and column indices.

        Parameters:
            row_index (int): The original row index.
            col_index (int): The original column index.

        Returns:
            tuple: The input row and column indices unchanged.
        """
        return row_index, col_index
