from datetime import datetime
from typing import Optional

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

    def __init__(self, _id: str, description: str, amount: float, category: str, date: datetime,
                 who: Optional[str] = None):
        """
        Initializes a Transaction object with the given parameters.
        """
        self.id: str = str(_id)
        self.description: str = str(description)
        self.amount: str = Formatter.format_amount(amount)
        self.category: str = Formatter.map_category(category)
        self.date: str = date.date().isoformat()
        self.who: str | None = who

    def to_list(self) -> list[str]:
        """
        Returns the transaction details as a list of strings.
        """
        res = [self.id, self.description, self.amount, Formatter.map_category(self.category), self.date]

        if self.who:
            res.append(self.who)

        return res

    @classmethod
    def from_db_row(cls, row: tuple) -> "TransactionEntity":
        """
        Maps a database row to a TransactionEntity instance.

        Args:
            row (list[str]): A tuple representing a transaction row from the database.

        Returns:
            TransactionEntity: The mapped TransactionEntity object.
        """
        # Extract data using descriptive variable names
        transaction_id, description, amount_str, category, date_field = row[:5]

        return cls(
            _id=str(transaction_id),
            description=str(description),
            amount=float(amount_str),
            category=str(category),
            date=cls._parse_date(date_field)
        )

    @staticmethod
    def _parse_date(date_field) -> datetime:
        """
        Parses a date field and converts it to a datetime object.

        Args:
            date_field (str | int | float): The date field to parse.

        Returns:
            datetime: Parsed datetime object.

        Raises:
            ValueError: If the date field is of an unsupported format or type.
        """
        if isinstance(date_field, str):
            try:
                return datetime.fromisoformat(date_field)  # ISO 8601 format
            except ValueError as e:
                raise ValueError(f"Invalid string format for date: {date_field}") from e
        elif isinstance(date_field, (int, float)):
            return datetime.fromtimestamp(date_field)  # UNIX timestamp
        else:
            raise ValueError(f"Unsupported date type: {type(date_field)}", date_field)
