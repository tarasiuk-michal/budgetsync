from datetime import datetime

from utils.fomatter import Formatter


class TransactionEntity:
    """
    A class representing a transaction entity.

    Attributes:
        id (str): Unique identifier for the transaction.
        description (str): A brief description of the transaction.
        amount (float): The monetary amount of the transaction.
        category (str): The category/type of the transaction.
        date (str): The date of the transaction in string format.
        who (str): The person or entity associated with the transaction.
    """

    def __init__(self, _id: str, description: str, amount: float, category: str, date: datetime, who: str):
        """
        Initializes a Transaction object with the given parameters.
        """
        self.id: str = _id
        self.description: str = description
        self.amount: str = Formatter.format_amount(amount)
        self.category: str = category
        self.date: str = date.date().isoformat()
        self.who: str = who

    def to_list(self) -> list[str]:
        """
        Returns the transaction details as a list of strings.
        """
        return [
            self.id,
            self.description,
            self.amount,
            Formatter.map_category(self.category),
            self.date,
            self.who,
        ]
