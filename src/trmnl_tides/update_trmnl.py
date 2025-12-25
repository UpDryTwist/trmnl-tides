"""Send our data to the TRMNL web hook."""
from __future__ import annotations

import requests

from .tides_data import NoaaTideData
from .weather_data import NoaaWeatherData

TRMNL_UUID = "trmnl-uuid"
TRMNL_URL = "https://usetrmnl.com/api/custom_plugins"
DEFAULT_STATION_ID = "8725520"  # Fort Myers, FL


class TRMNLUpdater:
    """Update the TRMNL web hook."""

    data : dict[str, str]

    def __init__(self) -> None:
        """Initialize the TRMNL Updater."""
        self.data = {}

    def create_data( self ) -> dict[str, str]:
        """
        Set up the data we want to send to TRMNL.  Get this from tide and weather
        objects.
        """
        tides = NoaaTideData(DEFAULT_STATION_ID)
        weather = NoaaWeatherData(DEFAULT_STATION_ID)
        tides.read_data()
        weather.read_data()
        data = {
            "next_high_tide": tides.next_high_tide.json(),
            "next_low_tide": tides.next_low_tide.json(),
            "weather": weather.json(),
        }
        return data

    def update(self) -> None:
        """
        Send the data to the TRMNL web hook.  Build the URL by adding our UUID,
        and send our variables as JSON data.
        """

        url = f"{TRMNL_URL}/{TRMNL_UUID}"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=self.data, headers=headers)
        response.raise_for_status()

