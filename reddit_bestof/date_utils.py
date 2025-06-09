import locale
from datetime import datetime, timedelta
from typing import Tuple

from dateutil.relativedelta import relativedelta


def get_timestamp_range(value: str) -> Tuple[str, int, int]:
    """Return the range of the report with a min and max timestamp.

    Example: for 2021-09-16, return the timestamp for 2021-09-15 21:00 and 2021-09-16 21:00
    """
    locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
    # TODO better timezone handling
    # needs to add 2 hours in order to have timestamp equivalent to the FR timezone.
    y, m, d = (int(x) for x in value.split("-", 3))
    max_datetime = datetime(y, m, d, 23, 0)
    min_datetime = max_datetime - timedelta(hours=24)
    formatted_date = f"du {datetime(y, m, d).strftime('%A %d %b %Y')}"
    return (
        formatted_date,
        int(min_datetime.timestamp()),
        int(max_datetime.timestamp()),
    )
