"""Module containing the pydantic classes used for getting the status of the station with a HTTP GET."""

from typing import List, Optional

from pydantic import BaseModel


class SessionStatus(BaseModel):
    """Displays the status of a station."""
    session_id: int
    allocated_power: float
    vehicle_max_power: float
    is_boosted: bool
    boosted_power: float
    active: bool


class ConnectorStatus(BaseModel):
    """Display the status of a connector of the charger."""
    connector_id: int
    session: Optional[SessionStatus]


class ChargerStatus(BaseModel):
    """Display the status of a charger."""
    charger_id: str
    max_power: float
    max_asked_power: float
    connectors: List[ConnectorStatus]


class SessionBoostStatus(BaseModel):
    """Display the status of a session boost applied by the battery."""
    sessionId: str
    boost: float


class BatteryStatus(BaseModel):
    """Display the status of the battery."""
    max_power: float
    state_of_charge: float
    session_boosts: List[SessionBoostStatus]


class StationStatus(BaseModel):
    """Display the status of the whole station. It is the result of the HTTP call."""
    station_id: str
    max_asked_power: float
    grid_capacity: float
    chargers: List[ChargerStatus]
    battery: Optional[BatteryStatus]
