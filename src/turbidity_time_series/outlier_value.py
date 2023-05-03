import numpy
import pandas
from typing import List, Union


def filter_invalid_value_according_to_abs_difference(
    value: float, other_values: List, abs_difference: float
) -> Union[float, None]:
    """
    Return None if the maximum absolute difference between the values and the other_values
    is greater that the accepted abs_difference. If it's lower, it returns the value
    """
    max_difference = numpy.abs(numpy.array(other_values) - value).max()
    if max_difference < abs_difference:
        return value
    else:
        return None


def filter_turbidity_according_to_rolling_window_and_max_difference(
    turbidity_series: pandas.Series, rolling_window: int, max_abs_difference: float
) -> List:
    """
    This function remove 'outlier' values from the turbidity series given in input.
    The rolling window need to be an odd number.
    For each value in the series, we will look at the value before & after according to the rolling window.
    Those values before and after, will be sent as well with the value of interest in the max_abs_difference
    to the function filter_invalid_value_according_to_abs_difference and filtered accordingly to that function
    """
    assert rolling_window % 2 == 1
    filtered_turbidity = []
    value_before_after = rolling_window // 2
    filtered_turbidity += [None] * value_before_after
    for i in range(value_before_after, len(turbidity_series) - value_before_after):
        value = turbidity_series[i]
        other_values = (
            turbidity_series[i - value_before_after : i].to_list()
            + turbidity_series[i + 1 : i + 1 + value_before_after].to_list()
        )
        filtered_value = filter_invalid_value_according_to_abs_difference(
            value, other_values, max_abs_difference
        )
        filtered_turbidity.append(filtered_value)
    filtered_turbidity += [None] * value_before_after
    return filtered_turbidity


def fill_none_value_with_local_interpolation(turbidity_series: pandas.Series) -> List:
    """
    Fill None value in a pandas.Series with a local interpolation.
    Since the neighbors might be None value as well, we start with a window of one value before/after.
    If all values are nan, we extend the windows by a step of one, untill we have valid values.
    """
    value_filtered_interpolated = []
    value_filtered_interpolated += [None]
    for i in range(1, len(turbidity_series) - 1):
        value = turbidity_series[i]
        k = 1
        while pandas.isna(value):
            value = numpy.nanmean(
                turbidity_series[i - k : i].to_list()
                + turbidity_series[i + 1 : i + 1 + k].to_list()
            )
            k += 1
        value_filtered_interpolated.append(value)
    value_filtered_interpolated += [None]
    return value_filtered_interpolated
