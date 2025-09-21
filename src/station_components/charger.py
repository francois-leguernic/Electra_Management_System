from .session import Session
from .statuses_models.models import ChargerStatus, ConnectorStatus


class Charger:
    """Modelizes the fast charger of Electra."""

    def __init__(self, label_id, max_power_capacity, nb_connectors):
        """Basic constructor, called at init."""
        self.label_id = label_id
        self.max_power_capacity = max_power_capacity
        self.nb_connectors = nb_connectors
        self.sessions = {}
        self.max_asked_power = 0
        self.non_boosted_sessions_count = 0
        self.boosted_sessions_count = 0

    def get_session(self, connectorId):
        """Return the session with id "connectorId"."""
        return self.sessions[connectorId]

    def remove_session(self, session_number):
        """Remove a session from the charger, when the session is closed."""
        if session_number in self.sessions:
            self.max_asked_power -= self.sessions[
                session_number
            ].get_max_vehicle_power()
            session = self.sessions[session_number]
            if session.is_battery_boosted:
                self.boosted_sessions_count -= 1
            else:
                self.non_boosted_sessions_count -= 1
            del self.sessions[session_number]

    def reallocate_session_optimally_from_charger(self):
        """Allocates maximum power possible in charger, either with uniformization, 
        or by allocating the maximum demand for each session.
        """
        if self.non_boosted_sessions_count > 0:
            if self.max_asked_power > self.max_power_capacity:
                newUniformPower = (
                    self.max_power_capacity / self.non_boosted_sessions_count
                )
                self.uniformize_powers_on_non_boosted_sessions(newUniformPower)
            else:
                self.for_each_non_boosted_session_allocate_max_power()

    def start_non_boosted_session(self, connectorId, vehicleMaxPower):
        """Start a usual session of the charger, with no use to the battery of the station."""
        self.max_asked_power += vehicleMaxPower
        if self.max_asked_power <= self.max_power_capacity:
            self.sessions[connectorId] = Session(
                connectorId, vehicleMaxPower, vehicleMaxPower
            )

        else:
            currentNbNonBoostedSessions = self.non_boosted_sessions_count
            currentNbNonBoostedSessions += 1
            uniformPower = self.max_power_capacity / currentNbNonBoostedSessions
            self.uniformize_powers_on_non_boosted_sessions(uniformPower)

            self.sessions[connectorId] = Session(
                connectorId, uniformPower, vehicleMaxPower
            )
        self.non_boosted_sessions_count += 1

    def start_boosted_session(self, connectorId, vehicleMaxPower, boost):
        """Start a session making use of the capacity of the battery."""
        self.sessions[connectorId] = Session(connectorId, 0, vehicleMaxPower)
        self.set_session_boosted(connectorId, boost)
        self.boosted_sessions_count += 1
        self.max_asked_power += vehicleMaxPower

    def uniformize_powers_on_non_boosted_sessions(self, power):
        """Apply the same power capacity to all non-boosted sessions."""
        for session in self.sessions:
            if not self.sessions[session].is_battery_boosted:
                self.sessions[session].set_power(power)
                
    def for_each_non_boosted_session_allocate_max_power(self):
        """Reallocates the max power demanded by the vehicle to each non-boosted session."""
        for session in self.sessions:
            sessionObject = self.sessions[session]
            if not self.sessions[session].is_battery_boosted:
                sessionObject.set_power(sessionObject.get_max_vehicle_power())

    def get_status(self):
        """Helper method used to display the status of the charger in the get status endpont."""
        connectors_status = []
        for i in range(1, self.nb_connectors + 1):
            if i in self.sessions:
                session_status = self.sessions[i].get_status()
            else:
                session_status = None
            connectors_status.append(
                ConnectorStatus(connector_id=i, session=session_status)
            )
        return ChargerStatus(
            charger_id=self.label_id,
            max_power=self.max_power_capacity,
            max_asked_power=self.max_asked_power,
            connectors=connectors_status,
        )

    def is_session_free(self, connectorId):
        """Checks if a session is already active."""
        return connectorId not in self.sessions

    def set_all_non_boosted_sessions_to(self, power):
        """Set all non-boosted sessions to "power" or the max possible. """
        maxLocalPower = 0
        if self.non_boosted_sessions_count > 0:
            maxLocalPower = self.max_power_capacity / self.non_boosted_sessions_count
        else:
            maxLocalPower = self.max_power_capacity
        for s in self.sessions:
            session = self.sessions[s]
            if not session.is_battery_boosted:
                session.set_power(min(power, maxLocalPower))

    def set_session_boosted(self, connectorId, boost):
        """Flag a session with id "connectorId" as boosted."""
        session = self.sessions[connectorId]
        session.flag_as_boosted(boost)

    def get_non_boosted_sessions_count(self):
        """Return the count of non-boosted sessions."""
        return self.non_boosted_sessions_count

    def get_boosted_sessions_count(self):
        """Return the count of boosted sessions."""
        return self.boosted_sessions_count
