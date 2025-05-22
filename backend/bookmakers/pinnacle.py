from .base import BookmakerBase

class Pinnacle(BookmakerBase):
    """Representa a casa de aposta Pinnacle."""
    NAME: str = "Pinnacle"
    DESCRIPTION: str = "Pinnacle, odds altas."
    ICON: str = "bi bi-graph-up"

    @staticmethod
    def get_info():
        return {
            "name": Pinnacle.NAME,
            "description": Pinnacle.DESCRIPTION,
            "icon": Pinnacle.ICON
        }
