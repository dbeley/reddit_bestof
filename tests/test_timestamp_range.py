from datetime import datetime

from reddit_bestof.date_utils import get_timestamp_range


def test_day_timestamp():
    result = (
        "du mardi 02 nov. 2021",
        int(datetime(2021, 11, 1, 23, 00).timestamp()),
        int(datetime(2021, 11, 2, 23, 00).timestamp()),
    )
    assert get_timestamp_range("2021-11-02") == result


def test_day_end_of_month_timestamp():
    result = (
        "du lundi 01 févr. 2021",
        int(datetime(2021, 1, 31, 23, 00).timestamp()),
        int(datetime(2021, 2, 1, 23, 00).timestamp()),
    )
    assert get_timestamp_range("2021-02-01") == result
