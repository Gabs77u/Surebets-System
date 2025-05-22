from .base import BookmakerBase

class Bet365(BookmakerBase):
    """Representa a casa de aposta Bet365."""
    NAME: str = "Bet365"
    DESCRIPTION: str = "Bet365, tradicional e confiável."
    ICON: str = "bi bi-cash-coin"

    @staticmethod
    def get_info():
        return {
            "name": Bet365.NAME,
            "description": Bet365.DESCRIPTION,
            "icon": Bet365.ICON
        }
