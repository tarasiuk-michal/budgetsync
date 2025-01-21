from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import config
from src.utils.enums import Categories
from src.utils.logger import Logging


class Formatter:
    """A utility class for formatting-related operations."""

    @staticmethod
    def format_timestamp(unix_timestamp: int) -> str:
        """Formats the UNIX timestamp into a human-readable date using the configured timezone."""
        try:
            local_tz = ZoneInfo(config.TIMEZONE)

            # Convert the timestamp to localized time
            localized_time = datetime.fromtimestamp(unix_timestamp, tz=local_tz)
            return localized_time.date().isoformat()
        except (ZoneInfoNotFoundError, ValueError, TypeError) as e:
            # Handle errors and provide fallback
            Logging.get_logger().error(
                f"Error formatting timestamp {unix_timestamp} with timezone '{config.TIMEZONE}': {e}"
            )
            return str(unix_timestamp)

    @staticmethod
    def format_amount(amount: float) -> str:
        """Formats the amount with a comma as the decimal separator."""
        if amount is None:
            raise ValueError("Amount cannot be None")
        return f"{amount:.2f}".replace(".", ",")

    @staticmethod
    def map_category(category_name: str) -> str:
        """Maps category foreign keys to their corresponding names."""
        cat: str = category_name.lower()
        return cat if Categories.is_category(cat) else 'inne'
