from .battery import Battery
from .charger import Charger
from .statuses_models.models import StationStatus


class Station:
    """Class to modelizes an Electra station."""

    def __init__(self, config):
        """Basic constructor."""
        self.name = config["stationId"]
        if "battery" in config:
            self.battery = self.addBattery(config["battery"])
        else:
            self.battery = None
        self.chargers = self.addChargers(config["chargers"])
        self.grid_capacity = config["gridCapacity"]
        self.max_asked_power = 0

    def addBattery(self, battery_config):
        """Add a BESS battery to the status at initialization."""
        return Battery(battery_config["initialCapacity"], battery_config["power"])

    def addChargers(self, chargersConfig):
        """Add the chargers configurations to the station, at initialization."""
        chargers = {}
        for config in chargersConfig:
            chargerId = config["id"]
            capacity = config["maxPower"]
            nbConnectors = config["connectors"]
            chargers[chargerId] = Charger(chargerId, capacity, nbConnectors)

        return chargers

    def get_charger(self, chargerId):
        """Return the charger with a specific Id."""
        if chargerId in self.chargers:
            return self.chargers[chargerId]

        else:
            return None

    def get_status(self):
        """Method to display the status of the station, used in the GET endpoint."""
        chargers_status = []
        for ch in self.chargers:
            charger = self.get_charger(ch)
            chargers_status.append(charger.get_status())

        return StationStatus(
            station_id=self.name,
            grid_capacity=self.grid_capacity,
            max_asked_power=self.max_asked_power,
            chargers=chargers_status,
            battery=self.battery.get_status() if self.battery else None,
        )

    def start_session_on_charger(self, chargerId, connectorId, maxVehiclePower):
        """Start a session on the charger, from HTTP call."""
        self.max_asked_power += maxVehiclePower
        charger = self.get_charger(chargerId)
        if self.max_asked_power <= self.grid_capacity:
            charger.start_non_boosted_session(connectorId, maxVehiclePower)
        if self.max_asked_power > self.grid_capacity:
            deficit = self.max_asked_power - self.grid_capacity
            if self.can_use_total_battery_boost(deficit):
                charger.start_boosted_session(connectorId, maxVehiclePower, deficit)
                self.battery.allocate_boost(chargerId, connectorId, maxVehiclePower)
            else:
                charger.start_non_boosted_session(connectorId, maxVehiclePower)
                self.set_all_non_boosted_sessions_to_uniform_power()

        self.recharge_battery_if_possible()

    def stop_session_on_charger(self, chargerId, connectorId):
        """Stop a session on a charger, from HTTP Call."""
        charger = self.get_charger(chargerId)
        session = charger.get_session(connectorId)
        if session.is_battery_boosted:
            self.battery.remove_battery_boost(chargerId, connectorId)
        self.max_asked_power -= session.max_vehicle_power
        charger.remove_session(connectorId)
        if self.max_asked_power > self.grid_capacity:
            self.set_all_non_boosted_sessions_to_uniform_power()
        else:
            [
                self.chargers[c].reallocate_session_optimally_from_charger()
                for c in self.chargers
            ]
        self.recharge_battery_if_possible()

    def set_all_non_boosted_sessions_to_uniform_power(self):
        """When the grid capacity is reached, the station applies, if possible, the 
        same uniform power to all non-boosted sessions."""
        activeSessions = self.get_number_non_boosted_sessions()
        
        uniform_power = self.grid_capacity / activeSessions
        for c in self.chargers:
            charger = self.chargers[c]
            charger.set_all_non_boosted_sessions_to(uniform_power)

    def get_number_non_boosted_sessions(self):
        """Return the number of non-boosted sessions across all-chargers."""
        return sum(
            [
                self.chargers[charger].get_non_boosted_sessions_count()
                for charger in self.chargers
            ]
        )

    def get_whole_capacity(self):
        """Return the power capacity at a given moment, taking battery into account."""
        return self.grid_capacity + self.battery.get_power()

    def can_use_total_battery_boost(self, deficit):
        """Checks if a battery boost can be used to fully allocate for a deficit."""
        return self.battery and self.battery.get_power() >= deficit

    def recharge_battery_if_possible(self):
        """If the grid capacity is not saturated, recharge the battery."""
        if (
            self.battery
            and (self.grid_capacity - self.max_asked_power) / self.grid_capacity >= 0.5
        ):
            self.battery.recharge()
