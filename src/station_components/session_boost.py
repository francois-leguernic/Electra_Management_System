from .statuses_models.models import SessionBoostStatus


class SessionBoost:
    """Helper class to modelize the boost allocated from BESS to a session."""
    def __init__(self, session_id, power_boost):
        self.power_boost = power_boost
        self.session_id = session_id

    def get_status(self):
        """Method called to display the status of the boost, in GET endpoint."""
        return SessionBoostStatus(sessionId=self.session_id,
                                   boost=self.power_boost)
