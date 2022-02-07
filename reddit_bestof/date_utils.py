from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Tuple


def get_timestamp_range(type: str, value: str) -> Tuple[str, int, int]:
    """Return the range of the report with a min and max timestamp.

    Example: for 2021-09-16, return the timestamp for 2021-09-15 21:00 and 2021-09-16 21:00
    """
    # TODO better timezone handling
    # needs to add 2 hours in order to have timestamp equivalent to the FR timezone.
    if type == "day":
        y, m, d = [int(x) for x in value.split("-", 3)]
        max_datetime = datetime(y, m, d, 23, 0)
        min_datetime = max_datetime - timedelta(hours=24)
        formatted_date = f"du {datetime(y, m, d).strftime('%A %d %b %Y')}"
    elif type == "month":
        y, m = [int(x) for x in value.split("-", 2)]
        max_datetime = (
            datetime(y + 1, 1, 1, 2, 0) if m == 12 else datetime(y, m + 1, 1, 2, 0)
        )
        min_datetime = max_datetime - relativedelta(months=1)
        formatted_date = f"du mois de {datetime(y, m, 1).strftime('%b %Y')}"
    elif type == "year":
        y = int(value)
        max_datetime = datetime(y + 1, 1, 1, 2, 0)
        min_datetime = max_datetime - relativedelta(years=1)
        formatted_date = f"de l'année {datetime(y, 1, 1).strftime('%Y')}"
    return (
        formatted_date,
        int(min_datetime.timestamp()),
        int(max_datetime.timestamp()),
    )
