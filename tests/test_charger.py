"""Unit tests covering features of the Charger component."""
import pytest

from src.station_components.charger import Charger


@pytest.fixture
def simple_charger():
    return Charger("CP001", 200, 2)


def test_start_non_boosted_sessions(simple_charger):
    simple_charger.start_non_boosted_session(1, 200)
    assert simple_charger.get_non_boosted_sessions_count() == 1
    assert simple_charger.get_session(1).allocated_power == 200
    simple_charger.start_non_boosted_session(2, 200)
    assert simple_charger.get_non_boosted_sessions_count() == 2

    session1 = simple_charger.get_session(1)
    session2 = simple_charger.get_session(2)
    assert session1.allocated_power == 100
    assert session2.allocated_power == 100

    assert simple_charger.max_asked_power == 400


def test_start_boosted_session(simple_charger):
    simple_charger.start_boosted_session(1, 200, 60)

    assert simple_charger.get_non_boosted_sessions_count() == 0
    assert simple_charger.get_boosted_sessions_count() == 1

    session = simple_charger.get_session(1)
    assert session.allocated_power == 0
    assert session.is_battery_boosted

    assert simple_charger.max_asked_power == 200
