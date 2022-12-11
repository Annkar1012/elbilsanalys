import datetime
import matplotlib.dates
import matplotlib.cm
import numpy as np
import pandas as pd

import defs

def plot_sorted_distance_per_day_stack(ax, distance_per_vehicle_per_day):
    bottom = np.zeros(len(distance_per_vehicle_per_day.index))
    for vehicle in distance_per_vehicle_per_day:
        vehicle_distance = distance_per_vehicle_per_day[vehicle]
        ax.bar(vehicle_distance.index, vehicle_distance, bottom=bottom, label=vehicle)
        bottom += vehicle_distance.to_numpy(na_value=0)
    ax.set_ylabel('Sträcka (km)')
    ax.legend(bbox_to_anchor=(1,1), loc="upper left")

def plot_total_distance_per_day(ax, distance_per_vehicle_per_day):
    total_distance_per_day = distance_per_vehicle_per_day.reset_index(drop=True)
    total_distance_per_day['sum'] = total_distance_per_day.sum(axis=1)
    total_distance_per_day.sort_values('sum', ascending=False, inplace=True)
    total_distance_per_day.drop(columns="sum", inplace=True)
    total_distance_per_day.reset_index(inplace=True, drop=True)

    bottom = np.zeros(len(total_distance_per_day.index))
    for vehicle in total_distance_per_day:
        vehicle_distance = total_distance_per_day[vehicle]
        ax.bar(vehicle_distance.index, vehicle_distance, bottom=bottom, label=vehicle)
        bottom += vehicle_distance.to_numpy(na_value=0)
    ax.legend(bbox_to_anchor=(1,1), loc="upper left")

def plot_total_distance_per_month(ax, distance_per_vehicle_per_day):
    distance_per_vehicle_per_month = distance_per_vehicle_per_day.groupby(distance_per_vehicle_per_day.index.month).sum()
    
    bottom = np.zeros(len(distance_per_vehicle_per_month.index))
    for vehicle in distance_per_vehicle_per_month:
        vehicle_distance = distance_per_vehicle_per_month[vehicle]
        months = [datetime.datetime.strptime(f"{m}", "%m") for m in vehicle_distance.index]
        ax.bar(months, vehicle_distance, bottom=bottom, label=vehicle, width=10)
        bottom += vehicle_distance.to_numpy(na_value=0)
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b'))
    ax.legend(bbox_to_anchor=(1,1), loc="upper left")

def plot_recommended_battery_size(ax, distance_per_day, battery_size, max_driving_distance, skipped_days):
    sorted_distance = distance_per_day.sort_values(ascending=False).reset_index(drop=True)
    ax.bar(sorted_distance.index, sorted_distance)

    ax.hlines(max_driving_distance, 0, skipped_days+5, 'k', label=battery_size)
    for dist, kwh, skip in zip(max_driving_distance, battery_size, skipped_days):
        ax.text(skip + 5, dist, f"{kwh:.0f} kWh ({skip} dagar)")

    ax.set_title(battery_size.name)
    ax.set_ylabel('Sträcka (km)')



def plot_usage_heatmap(ax, vehicle_data, tick_formatter, colormap):
    for weekday_number, daily_data in vehicle_data.groupby(level=0):
        daily_data = daily_data.droplevel(0)
        daily_data.set_index(daily_data.index.to_series().apply(lambda d: pd.to_datetime(d.isoformat())), inplace=True)
        daily_data["dur"] = pd.to_timedelta(defs.TIME_BINS)
        xvalues = list(zip(daily_data.index, daily_data['dur']))
        ax.broken_barh(xvalues, (weekday_number-0.25, 0.75), color=colormap.to_rgba(daily_data[vehicle_data.columns[0]]))
    ax.xaxis.set_major_formatter(tick_formatter)
    ax.set_yticks(range(7))
    ax.set_yticklabels(defs.WEEKDAYS)
    ax.set_title(vehicle_data.columns[0])