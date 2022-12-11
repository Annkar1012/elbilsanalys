import math
import pandas as pd
import numpy as np

from defs import Col, PERCENTILES, HIGH_ENERGY_CONSUMPTION, DEPTH_OF_DISCHARGE, TIME_BINS


def pivot_to_distance_per_vehicle_per_day(data):
    # Skapa pivottabell med fordon som kolumner, datum som radindex och körsträcka som fält
    distance_per_vehicle_per_day = pd.pivot_table(data, values=Col.DISTANCE, index=Col.START_DATE, columns=Col.VEHICLE, aggfunc=np.sum)
    distance_per_vehicle_per_day.index = pd.DatetimeIndex(distance_per_vehicle_per_day.index)
    return distance_per_vehicle_per_day.columns.size, distance_per_vehicle_per_day

def longest_typical_driving_distance(distance_per_vehicle_per_day: pd.DataFrame):
    max_distances = pd.DataFrame(index=distance_per_vehicle_per_day.columns, columns=PERCENTILES)
    skipped_days = pd.DataFrame(index=distance_per_vehicle_per_day.columns, columns=PERCENTILES)
    for vehicle in distance_per_vehicle_per_day:
        sorted_distance = distance_per_vehicle_per_day[vehicle].dropna().sort_values(ascending=False)
        driving_days = sorted_distance.count()
        days_to_count = [math.ceil(d) for d in driving_days * PERCENTILES]
        max_distance = [sorted_distance[-index] for index in days_to_count]
        max_distances.at[vehicle] = max_distance
        skipped_days.at[vehicle] = [sorted_distance.size - d for d in days_to_count]
    return max_distances, skipped_days

def calculate_recommended_battery_capacity(driving_distance: pd.Series):
    return [d*HIGH_ENERGY_CONSUMPTION/DEPTH_OF_DISCHARGE for d in driving_distance]

def time_bin_df(data):
    df_time = data[["row_n", Col.START_TIME, Col.END_TIME]].set_index("row_n").stack().reset_index(level=-1, drop=True).rename('time').to_frame()
    df_time = df_time.groupby('row_n').apply(lambda x: x.set_index('time').resample(TIME_BINS).asfreq()).reset_index()

    df_time['Datum'] = pd.DatetimeIndex(df_time['time']).date
    df_time['Tid'] = pd.DatetimeIndex(df_time['time']).time
    return df_time

def bin_vehicle_usage(vehicles, data, df_time):
    binned = []
    for vehicle in vehicles:
        data_for_vehicle = data.where(data[Col.VEHICLE] == vehicle).drop(columns=[Col.DISTANCE, Col.VEHICLE]).dropna()
        binned.append(df_time.merge(data_for_vehicle[['row_n', Col.WEEKDAY]]).groupby([Col.WEEKDAY, 'Tid'])["Datum"].count().to_frame().rename(columns={"Datum": vehicle}))

    binned_all = binned[0]
    if len(binned) > 1:
        binned_all = binned_all.join(binned[1:], how='outer')
        binned_all.fillna(0, inplace=True)

    return binned_all