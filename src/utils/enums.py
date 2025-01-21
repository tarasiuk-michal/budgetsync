from enum import Enum


class Categories(Enum):
    """
    Defines an enumeration to categorize items or expenditures.

    The Categories class represents predefined category values like
    "spożywcze", "transport", and more. It provides methods for accessing
    category values and validating the existence of a category.
    """
    SPOŻYWCZE = 'spożywcze'
    TRANSPORT = 'transport'
    PRZYJEMNOŚCI = 'przyjemności'
    INNE = 'inne'
    RACHUNKI = 'rachunki'

    @classmethod
    def get(cls) -> list[str]:
        """
        Retrieve all category values.

        :return: A list of all category values.
        :rtype: list[str]
        """
        return [category.value for category in cls]

    @classmethod
    def is_category(cls, category: str) -> bool:
        """
        Check if a given category is valid.

        :param category: The category to check.
        :type category: str
        :return: True if the category is valid, False otherwise.
        :rtype: bool
        """
        return category in cls.get()
