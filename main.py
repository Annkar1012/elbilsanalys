import matplotlib.pyplot as plt
import matplotlib.dates
import matplotlib.cm
import numpy as np
import pandas as pd
import sys

import plots
import util
from defs import Col, FILTER, TIME_BINS, WEEKDAYS, COLORSCHEME

try:
    file = util.ask_file()
    data = pd.read_csv(file, delimiter=";", decimal=',', usecols=FILTER)
except FileNotFoundError:
    sys.exit(0)

data['row_n'] = range(len(data))
data[Col.START_TIME] = pd.to_datetime(data[Col.START_DATE] + ' ' + data[Col.START_TIME])
data[Col.END_TIME] = pd.to_datetime(data[Col.END_DATE] + ' ' + data[Col.END_TIME])
data[Col.WEEKDAY] = pd.DatetimeIndex(data[Col.START_DATE]).weekday # Monday == 0
data["Duration"] = data[Col.END_TIME] - data[Col.START_TIME]


n_vehicles, distance_per_vehicle_per_day = util.pivot_to_distance_per_vehicle_per_day(data)
max_driving_distance, skipped_days = util.longest_typical_driving_distance(distance_per_vehicle_per_day)
recommended_battery_size_kWh = max_driving_distance.transform(util.calculate_recommended_battery_capacity)

vehicle_ids = list(distance_per_vehicle_per_day)

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

plots.plot_sorted_distance_per_day_stack(ax1, distance_per_vehicle_per_day)

plots.plot_total_distance_per_day(ax2, distance_per_vehicle_per_day)

plots.plot_total_distance_per_month(ax3, distance_per_vehicle_per_day)


fig, axs = plt.subplots(n_vehicles, 1, sharex='col', squeeze=False)

for ax, vehicle in zip(axs[:, 0], distance_per_vehicle_per_day):
    plots.plot_recommended_battery_size(ax,
                                        distance_per_vehicle_per_day[vehicle],
                                        recommended_battery_size_kWh.loc[vehicle],
                                        max_driving_distance.loc[vehicle],
                                        skipped_days.loc[vehicle])


df_time = util.time_bin_df(data)
binned_all = util.bin_vehicle_usage(vehicle_ids, data, df_time)

fig, axs = plt.subplots(n_vehicles, 1, sharex='col', squeeze=False)
tick_formatter = matplotlib.dates.DateFormatter('%H:%M:%S') 
norm = matplotlib.colors.Normalize(vmin=1, vmax=np.amax(binned_all.max(axis=0)))
colormap = matplotlib.cm.ScalarMappable(norm=norm, cmap=COLORSCHEME)

for ax, vehicle in zip(axs[:, 0], binned_all):
    plots.plot_usage_heatmap(ax, binned_all[[vehicle]], tick_formatter, colormap)

fig.colorbar(colormap, location="bottom", ax=axs[-1])

plt.show()
