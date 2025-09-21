"""Unit tests covering features around the Station component."""
import pytest

from src.station_components.station import Station


@pytest.fixture
def simple_station_no_battery():
    config = {
        "stationId": "Test Electra Station",
        "gridCapacity": 400,
        "chargers": [{"id": "CP001", "maxPower": 300, "connectors": 2}],
        "battery": {"initialCapacity": 200, "power": 200},
    }
    return Station(config)


@pytest.fixture
def simple_station_with_battery():
    config = {
        "stationId": "Test Electra Station",
        "gridCapacity": 300,
        "chargers": [{"id": "CP001", "maxPower": 300, "connectors": 2}],
        "battery": {"initialCapacity": 200, "power": 200},
    }
    return Station(config)


def test_simple_uniformisation_two_vehicles(simple_station_no_battery):
    simple_station_no_battery.start_session_on_charger("CP001", 1, 200)
    assert simple_station_no_battery.max_asked_power == 200

    charger = simple_station_no_battery.get_charger("CP001")
    assert charger.get_non_boosted_sessions_count() == 1
    assert charger.get_boosted_sessions_count() == 0

    simple_station_no_battery.start_session_on_charger("CP001", 2, 200)

    charger = simple_station_no_battery.get_charger("CP001")
    assert charger.get_non_boosted_sessions_count() == 2
    assert charger.get_boosted_sessions_count() == 0

    for session in charger.sessions:
        assert charger.sessions[session].get_power() == 150


def test_simple_cannot_use_battery(simple_station_with_battery):
    simple_station_with_battery.start_session_on_charger("CP001", 1, 200)
    assert simple_station_with_battery.max_asked_power == 200

    charger = simple_station_with_battery.get_charger("CP001")
    assert charger.get_non_boosted_sessions_count() == 1
    assert charger.get_boosted_sessions_count() == 0

    simple_station_with_battery.start_session_on_charger("CP001", 2, 150)

    charger = simple_station_with_battery.get_charger("CP001")
    assert charger.get_non_boosted_sessions_count() == 2
    assert charger.get_boosted_sessions_count() == 0

    session1 = charger.get_session(1)
    session2 = charger.get_session(2)

    assert session1.allocated_power == 150
    assert not session1.is_battery_boosted
    assert session1.max_vehicle_power == 200

    assert session2.allocated_power == 150
    assert not session2.is_battery_boosted
    assert session2.max_vehicle_power == 150


def test_simple_can_use_battery(simple_station_with_battery):
    simple_station_with_battery.start_session_on_charger("CP001", 1, 20)
    assert simple_station_with_battery.max_asked_power == 20

    simple_station_with_battery.stop_session_on_charger("CP001", 1)
    assert simple_station_with_battery.max_asked_power == 0

    simple_station_with_battery.start_session_on_charger("CP001", 2, 20)
    assert simple_station_with_battery.max_asked_power == 20

    simple_station_with_battery.stop_session_on_charger("CP001", 2)
    assert simple_station_with_battery.max_asked_power == 0

    assert simple_station_with_battery.battery.state_of_charge == 40

    simple_station_with_battery.start_session_on_charger("CP001", 1, 200)
    assert simple_station_with_battery.max_asked_power == 200

    charger = simple_station_with_battery.get_charger("CP001")
    assert charger.get_non_boosted_sessions_count() == 1
    assert charger.get_boosted_sessions_count() == 0

    simple_station_with_battery.start_session_on_charger("CP001", 2, 150)

    charger = simple_station_with_battery.get_charger("CP001")
    assert charger.get_non_boosted_sessions_count() == 1
    assert charger.get_boosted_sessions_count() == 1

    session1 = charger.get_session(1)
    session2 = charger.get_session(2)

    assert session1.allocated_power == 200
    assert not session1.is_battery_boosted
    assert session1.max_vehicle_power == 200

    assert session2.allocated_power == 0
    assert session2.is_battery_boosted == True
    assert session2.max_vehicle_power == 150
