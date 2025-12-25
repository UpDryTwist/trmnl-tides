"""Data reader for tides information."""

from __future__ import annotations

import os
from enum import Enum
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import noaa_coops


CURRENT_TIMEZONE = "America/New_York"


class TidePhase(Enum):
    """Define the different phases for a tide."""

    UNKNOWN = "Unknown"
    HIGH = "High Tide"
    FLOOD = "Flood Tide"
    LOW = "Low Tide"
    EBB = "Ebb Tide"
    SPRING = "Spring Tide"
    NEAP = "Neap Tide"


class TideDataPoint:
    """Data point for tide information."""

    def __init__(
        self,
        tide_date: date,
        tide_time: time,
        height: float,
        location_id: str,
    ) -> None:
        """Initialize the data point."""
        self.tide_date = tide_date
        self.tide_time = tide_time
        self.height = height
        self.location_id = location_id
        self.tide_phase = TidePhase.UNKNOWN

    def __str__(self) -> str:
        """Render simple string representation of the data point."""
        return f"{self.tide_date} {self.tide_time} {self.height} {self.tide_phase}"

    def json(self) -> dict[str, str]:
        """Return a JSON representation of the data point."""
        return {
            "tide_date": self.tide_date,
            "tide_time": self.tide_time,
            "height": self.height,
            "location_id": self.location_id,
            "tide_phase": self.tide_phase,
        }


class TideData:
    """Collection of TideDataPoint objects."""

    def __init__(self) -> None:
        """Initialize the collection."""
        self.data = []
        self.next_low_tide = None
        self.next_high_tide = None

    def add_data_point(self, data_point: TideDataPoint) -> None:
        """Add a data point to the collection."""
        self.data.append(data_point)

    def __str__(self) -> str:
        """Render simple string representation of the data."""
        return "\n".join(str(data_point) for data_point in self.data)

    def json(self) -> list[dict[str, str]]:
        """Return a JSON representation of the data."""
        return [data_point.json() for data_point in self.data]


class NoaaTideData(TideData):
    """Data reader for NOAA tide information."""

    def __init__(self, location_id: str) -> None:
        """Initialize the data reader."""
        super().__init__()
        self.location_id = location_id

    @staticmethod
    def set_tide_phase(
        last_data_point: TideDataPoint | None,
        data_point: TideDataPoint,
    ) -> None:
        """Set the tide phase for the data point based on what our prior data point was."""
        if last_data_point is not None:
            if data_point.height > last_data_point.height:
                if last_data_point.tide_phase == TidePhase.EBB:
                    last_data_point.tide_phase = TidePhase.LOW
                elif last_data_point.tide_phase == TidePhase.UNKNOWN:
                    last_data_point.tide_phase = TidePhase.FLOOD
                data_point.tide_phase = TidePhase.FLOOD
            elif data_point.height < last_data_point.height:
                if last_data_point.tide_phase == TidePhase.FLOOD:
                    last_data_point.tide_phase = TidePhase.HIGH
                elif last_data_point.tide_phase == TidePhase.UNKNOWN:
                    last_data_point.tide_phase = TidePhase.EBB
                data_point.tide_phase = TidePhase.EBB
            else:
                data_point.tide_phase = last_data_point.tide_phase
        else:
            data_point.tide_phase = TidePhase.UNKNOWN

    def read_data(self) -> None:
        """Read data from NOAA."""
        self.next_low_tide = None
        self.next_high_tide = None
        station = noaa_coops.Station(self.location_id)
        data = station.get_data(
            begin_date=datetime.now(ZoneInfo(os.environ.get("TZ", CURRENT_TIMEZONE))).strftime("%Y%m%d %H:%M"),  # noqa: DTZ011
            end_date=(datetime.now(ZoneInfo(os.environ.get("TZ", CURRENT_TIMEZONE))) + timedelta(days=1)).strftime("%Y%m%d %H:%M"),  # noqa: DTZ011
            product="predictions",
            datum="MLLW",
            units="english",
            time_zone="lst_ldt",
        )
        last_data_point = None
        for row in data.itertuples():
            tide_date = row.Index.date()  # type: ignore[attr-defined]
            tide_time = row.Index.time()  # type: ignore[attr-defined]
            height = row.v  # type: ignore[attr-defined]
            data_point = TideDataPoint(tide_date, tide_time, height, self.location_id)
            self.add_data_point(data_point)
            self.set_tide_phase(last_data_point, data_point)
            if last_data_point:
                if last_data_point.tide_phase == TidePhase.LOW and not self.next_low_tide:
                    self.next_low_tide = last_data_point
                elif last_data_point.tide_phase == TidePhase.HIGH and not self.next_high_tide:
                    self.next_high_tide = last_data_point
            last_data_point = data_point
