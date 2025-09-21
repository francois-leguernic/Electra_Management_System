from .session_boost import SessionBoost
from .statuses_models.models import BatteryStatus


class Battery:
    """Modelize the battery used to avoid peak shaving."""

    def __init__(self, initial_capacity, power):
        """Constructor of the battery, called at init."""
        self.initial_capacity = initial_capacity
        self.max_power = power
        self.state_of_charge = 0
        self.session_boosts = {}

    def get_status(self):
        """Method used in the GET endpoint to display battery's status."""
        sessionBoosts = []
        for boost in self.session_boosts:
            sessionBoosts.append(self.session_boosts[boost].get_status())
        return BatteryStatus(
            max_power=self.max_power,
            state_of_charge=self.state_of_charge,
            session_boosts=sessionBoosts,
        )

    def get_power(self):
        "Returns the available power of the battery, if usable."
        if self.state_of_charge >= 20:
            return self.max_power
        return 0

    def allocate_boost(self, chargerId, connectorId, powerBoost):
        """Adds a session boost to the state of the battery. Will be used in display."""
        sessionKey = str(chargerId) + "_" + str(connectorId)
        self.session_boosts[sessionKey] = SessionBoost(
            str(chargerId) + "_" + str(connectorId), powerBoost
        )
        self.state_of_charge = 0

    def recharge(self):
        """Increments the state of charge of the battery."""
        if self.state_of_charge <= 90:
            self.state_of_charge += 10

    def remove_battery_boost(self, chargerId, connectorId):
        """Remove a session boost when the session is closed."""
        del self.session_boosts[str(chargerId) + "_" + str(connectorId)]
