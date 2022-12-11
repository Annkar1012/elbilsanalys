import matplotlib.cm
import numpy as np

HIGH_ENERGY_CONSUMPTION = 0.25 # kWh/km
DEPTH_OF_DISCHARGE = 0.7
PERCENTILES = np.array([1, 0.98, 0.95])

TIME_BINS = "10T" # 10 minutes
COLORSCHEME = matplotlib.cm.BuPu

WEEKDAYS = ['Må', 'Ti', 'On', 'To', 'Fr', 'Lö', 'Sö']


class Col:
    DISTANCE = "Sträcka(km)"
    START_DATE = "Startdatum"
    START_TIME = "Starttid"
    END_DATE = "Slutdatum"
    END_TIME = "Sluttid"
    VEHICLE = "Fordon"
    WEEKDAY = "Veckodag"

FILTER = [Col.START_DATE, Col.START_TIME, Col.END_DATE, Col.END_TIME, Col.VEHICLE, Col.DISTANCE]