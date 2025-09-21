from .statuses_models.models import SessionStatus


class Session:
    """Component modelizing the active connections 
    between a charger and a vehicle."""
    def __init__(self, label_id, power, max_vehicle_power):
        """Basic constructor."""
        self.label_id = label_id
        self.allocated_power = power
        self.max_vehicle_power = max_vehicle_power
        self.is_battery_boosted = False
        self.boosted_power = 0

    def set_power(self, power):
        """Set the power allocated to a session."""
        if power > self.max_vehicle_power:
            self.allocated_power = self.max_vehicle_power
        else:
            self.allocated_power = power

    def get_power(self):
        """Return the power allocated to a session."""
        return self.allocated_power

    def get_status(self):
        """Method used to display the status of a method, in the GET endpoint."""
        return SessionStatus(
            session_id=self.label_id,
            allocated_power=self.allocated_power,
            vehicle_max_power=self.max_vehicle_power,
            is_boosted=self.is_battery_boosted,
            boosted_power=self.boosted_power,
            active=True,
        )

    def get_max_vehicle_power(self):
        """Return the max power demanded by the vehicle of the session."""
        return self.max_vehicle_power

    def flag_as_boosted(self, boostedPower):
        """Flag the session as boosted."""
        self.is_battery_boosted = True
        self.allocated_power = 0
        self.boosted_power = boostedPower
