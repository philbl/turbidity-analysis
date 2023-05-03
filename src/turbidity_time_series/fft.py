from numpy.fft import rfft, rfftfreq
import pandas
import matplotlib.pyplot as plt


def calculate_and_plot_fft(series: pandas.Series, series_name: str, ax: plt.Axes):
    """
    calculate and plot the fft. This is make to do when we have value every hours.
    """
    fft = abs(rfft(series))
    fft_freq = rfftfreq(len(series), d=1.0 / 24.0)
    ax.plot(fft_freq[2:], fft[2:])
    ax.set_xticks(list(range(13)))
    ax.set_xlabel("frequency (1/Day)")
    ax.set_title(f"FFT for {series_name}")
