import matplotlib.pyplot as plt
from pathlib import Path

from src.turbidity_time_series.outlier_value import (
    filter_turbidity_according_to_rolling_window_and_max_difference,
    fill_none_value_with_local_interpolation,
)
from src.turbidity_time_series.fft import calculate_and_plot_fft


def plot_and_save_all_figure(
    data, max_abs_difference, estuary_name, rolling_window=3, filter_after_nrow=None
):
    """
    This is the main function in the turbidity_time_series.
    It plots:
        The value of the filtered then interpolated turbidity series,
        The values of the fft for the filtered then interpolated turbidity series
        The values of the fft for the temperature
    """
    data[
        "filtered_turbidity"
    ] = filter_turbidity_according_to_rolling_window_and_max_difference(
        data["turbidity"], rolling_window, max_abs_difference
    )
    data["filtered_interpolated_turbidity"] = fill_none_value_with_local_interpolation(
        data["filtered_turbidity"]
    )
    data = data[~data["filtered_interpolated_turbidity"].isna()]
    if filter_after_nrow is not None:
        data = data[:filter_after_nrow]
    data = data.reset_index(drop=True)

    fig, axs = plt.subplots(3, 1, figsize=(12, 15))
    axs[0].plot(
        data["date"],
        data["filtered_interpolated_turbidity"],
        label="Interpolated Value",
    )
    axs[0].plot(data["date"], data["filtered_turbidity"], label="Real Value")
    axs[0].legend()
    axs[0].tick_params(axis="x", labelrotation=45)
    axs[0].set_title("Variation of Turbidity")
    fig.suptitle(
        f"Values that varies more than {max_abs_difference} NTU between two measurements are filtered\n"
        f"{round(data['filtered_turbidity'].isna().mean(), 4)*100}% of value are filtered\n"
        "local interpolation is then used",
        fontsize="small",
    )
    calculate_and_plot_fft(
        data["filtered_interpolated_turbidity"], f"Turbidity at {estuary_name}", axs[1]
    )
    calculate_and_plot_fft(data["temp"], f"Temperature at {estuary_name}", axs[2])
    plt.tight_layout()
    Path(f"images/{estuary_name}").mkdir(exist_ok=True)
    plt.savefig(
        f"images/{estuary_name}/{estuary_name}_fft_{max_abs_difference}_filtering.png"
    )
    plt.close()
