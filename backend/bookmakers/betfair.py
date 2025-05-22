from .base import BookmakerBase

class Betfair(BookmakerBase):
    """Representa a casa de aposta Betfair."""
    NAME: str = "Betfair"
    DESCRIPTION: str = "Betfair, bolsa de apostas."
    ICON: str = "bi bi-arrow-left-right"

    @staticmethod
    def get_info():
        return {
            "name": Betfair.NAME,
            "description": Betfair.DESCRIPTION,
            "icon": Betfair.ICON
        }
