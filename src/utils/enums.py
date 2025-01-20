from enum import Enum


class Categories(Enum):
    SPOŻYWCZE = 'spożywcze'
    TRANSPORT = 'transport'
    PRZYJEMNOŚCI = 'przyjemności'
    INNE = 'inne'
    RACHUNKI = 'rachunki'

    @classmethod
    def get(cls):
        return [category.value for category in cls]

    @classmethod
    def is_category(cls, category):
        return category in cls.get()
