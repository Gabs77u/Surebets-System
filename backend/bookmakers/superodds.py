from .base import BookmakerBase

class SuperOdds(BookmakerBase):
    """Representa a casa de aposta Super Odds."""
    NAME: str = "Super Odds"
    DESCRIPTION: str = "Super Odds, promoções especiais."
    ICON: str = "bi bi-star-fill"

    @staticmethod
    def get_info():
        return {
            "name": SuperOdds.NAME,
            "description": SuperOdds.DESCRIPTION,
            "icon": SuperOdds.ICON
        }
