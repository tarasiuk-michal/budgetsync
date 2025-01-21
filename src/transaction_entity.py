from datetime import datetime

from src.utils.fomatter import Formatter


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

    def __init__(self, _id: str, description: str, amount: float, category: str, date: datetime, who: str = None):
        """
        Initializes a Transaction object with the given parameters.
        """
        self.id: str = str(_id)
        self.description: str = str(description)
        self.amount: str = Formatter.format_amount(amount)
        self.category: str = Formatter.map_category(category)
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

    @classmethod
    def from_db_row(cls, row: tuple) -> "TransactionEntity":
        """
        Maps a database row to a TransactionEntity instance.

        Args:
            row (list[str]): A tuple representing a transaction row from the database.

        Returns:
            TransactionEntity: The mapped TransactionEntity object.
        """
        date = None
        if isinstance(row[4], str):
            date = datetime.fromisoformat(row[4])
        elif isinstance(row[4], int) or isinstance(row[4], float):
            date = datetime.fromtimestamp(row[4])

        return cls(
            _id=row[0],  # ID of the transaction
            description=row[1],  # Description of the transaction
            amount=float(row[2]),  # Transaction amount
            category=row[3],  # Transaction category
            date=date  # Transaction date
        )
