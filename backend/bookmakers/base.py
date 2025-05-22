from typing import Dict

class BookmakerBase:
    """Classe base para casas de apostas."""
    NAME: str = ""
    DESCRIPTION: str = ""
    ICON: str = ""

    @classmethod
    def get_info(cls) -> Dict[str, str]:
        return {
            "name": cls.NAME,
            "description": cls.DESCRIPTION,
            "icon": cls.ICON
        }
