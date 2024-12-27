"""Tests for the trmnl_tides.tides_data module."""

from datetime import date, time

from trmnl_tides.tides_data import NoaaTideData, TideData, TideDataPoint, TidePhase


def test_tide_data_point() -> None:
    """Test basic functionality of the TideDataPoint class."""
    tide_date = date(2023, 10, 1)
    tide_time = time(12, 0)
    height = 5.0
    location_id = "9447130"
    data_point = TideDataPoint(tide_date, tide_time, height, location_id)

    assert data_point.tide_date == tide_date
    assert data_point.tide_time == tide_time
    assert data_point.height == height
    assert data_point.location_id == location_id
    assert data_point.tide_phase == TidePhase.UNKNOWN


def test_tide_data() -> None:
    """Test basic functionality of the TideData class."""
    tide_data = TideData()
    assert len(tide_data.data) == 0

    tide_date = date(2023, 10, 1)
    tide_time = time(12, 0)
    height = 5.0
    location_id = "9447130"
    data_point = TideDataPoint(tide_date, tide_time, height, location_id)
    tide_data.add_data_point(data_point)

    assert len(tide_data.data) == 1
    assert tide_data.data[0] == data_point


def test_noaa_tide_data() -> None:
    """Test basic functionality of the NoaaTideData class."""
    noaa_tide_data = NoaaTideData("9447130")
    assert noaa_tide_data.location_id == "9447130"
    assert len(noaa_tide_data.data) == 0


def test_set_tide_phase() -> None:
    """Test setting the tide phase based on the prior data point."""
    tide_date = date(2023, 10, 1)
    tide_time = time(12, 0)
    location_id = "9447130"

    data_point1 = TideDataPoint(tide_date, tide_time, 5.0, location_id)
    data_point2 = TideDataPoint(tide_date, tide_time, 6.0, location_id)
    NoaaTideData.set_tide_phase(None, data_point1)
    assert data_point1.tide_phase == TidePhase.UNKNOWN

    NoaaTideData.set_tide_phase(data_point1, data_point2)
    assert data_point1.tide_phase == TidePhase.FLOOD
    assert data_point2.tide_phase == TidePhase.FLOOD

    data_point3 = TideDataPoint(tide_date, tide_time, 4.0, location_id)
    NoaaTideData.set_tide_phase(data_point2, data_point3)
    assert data_point2.tide_phase == TidePhase.HIGH
    assert data_point3.tide_phase == TidePhase.EBB
