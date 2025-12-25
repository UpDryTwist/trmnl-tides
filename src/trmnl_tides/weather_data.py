"""Weather data module."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import noaa_coops

if TYPE_CHECKING:
    import pandas as pd

CURRENT_TIMEZONE = "America/New_York"


class WeatherData:
    """Weather data class."""

    def __init__(self) -> None:
        """Initialize the weather data class."""
        self.weather_time = datetime.now(
            ZoneInfo(os.environ.get("TZ", CURRENT_TIMEZONE)),
        )
        self.air_temperature = 0.0
        self.water_temperature = 0.0
        self.barometric_pressure = 0.0
        self.wind_speed_knots = 0.0
        self.wind_direction = ""
        self.wind_speed_gust_knots = 0.0

    def __str__(self) -> str:
        """Render simple string representation of the weather data."""
        return (
            f"Time: {self.weather_time}\n"
            f"Air Temp: {self.air_temperature} °F\n"
            f"Water Temp: {self.water_temperature} °F\n"
            f"Barometric Pressure: {self.barometric_pressure} mbars\n"
            f"Wind: {self.wind_speed_knots} knots from the {self.wind_direction} gusting to {self.wind_speed_gust_knots}\n"
        )

    def json(self) -> dict[str, str]:
        """Return a JSON representation of the weather data."""
        return {
            "weather_time": self.weather_time,
            "air_temperature": self.air_temperature,
            "water_temperature": self.water_temperature,
            "barometric_pressure": self.barometric_pressure,
            "wind_speed_knots": self.wind_speed_knots,
            "wind_direction": self.wind_direction,
            "wind_speed_gust_knots": self.wind_speed_gust_knots,
        }

class NoaaWeatherData(WeatherData):
    """NOAA weather data class."""

    def __init__(self, location_id: str) -> None:
        """Initialize the NOAA weather data class."""
        super().__init__()
        self.location_id = location_id

    @staticmethod
    def fetch_reading(station: noaa_coops.Station, product: str) -> pd.Series:
        """Fetch a reading from the NOAA API.  Give ourselves a bit of a time buffer."""
        start_time = (
            datetime.now(ZoneInfo(os.environ.get("TZ", CURRENT_TIMEZONE)))
            + timedelta(minutes=-15)
        ).strftime("%Y%m%d %H:%M")
        end_time = datetime.now(
            ZoneInfo(os.environ.get("TZ", CURRENT_TIMEZONE)),
        ).strftime("%Y%m%d %H:%M")
        data = station.get_data(
            begin_date=start_time,
            end_date=end_time,
            product=product,
            units="english",
            time_zone="lst_ldt",
        )
        return data.iloc[0]

    def read_data(self) -> None:
        """Read weather data from NOAA."""
        station = noaa_coops.Station(self.location_id)
        row = self.fetch_reading(station, "air_temperature")
        self.air_temperature = row.v  # type: ignore[attr-defined]
        row = self.fetch_reading(station, "water_temperature")
        self.water_temperature = row.v
        row = self.fetch_reading(station, "air_pressure")
        self.barometric_pressure = row.v
        row = self.fetch_reading(station, "wind")
        self.wind_speed_knots = row.s
        self.wind_direction = row.dr
        self.wind_speed_gust_knots = row.g
        self.weather_time = datetime.now(
            ZoneInfo(os.environ.get("TZ", CURRENT_TIMEZONE)),
        )
