from datetime import datetime
from reddit_bestof.date_utils import get_timestamp_range


def test_day_timestamp():
    result = (
        "du Tuesday 02 Nov 2021",
        int(datetime(2021, 11, 1, 23, 00).timestamp()),
        int(datetime(2021, 11, 2, 23, 00).timestamp()),
    )
    assert get_timestamp_range("day", "2021-11-02") == result


def test_day_end_of_month_timestamp():
    result = (
        "du Monday 01 Feb 2021",
        int(datetime(2021, 1, 31, 23, 00).timestamp()),
        int(datetime(2021, 2, 1, 23, 00).timestamp()),
    )
    assert get_timestamp_range("day", "2021-02-01") == result


def test_month_timestamp():
    result = (
        "du mois de Mar 2021",
        int(datetime(2021, 3, 1, 2, 00).timestamp()),
        int(datetime(2021, 4, 1, 2, 00).timestamp()),
    )
    assert get_timestamp_range("month", "2021-03") == result


def test_month_december_timestamp():
    result = (
        "du mois de Dec 2021",
        int(datetime(2021, 12, 1, 2, 00).timestamp()),
        int(datetime(2022, 1, 1, 2, 00).timestamp()),
    )
    assert get_timestamp_range("month", "2021-12") == result


def test_month_january_timestamp():
    result = (
        "du mois de Jan 2022",
        int(datetime(2022, 1, 1, 2, 00).timestamp()),
        int(datetime(2022, 2, 1, 2, 00).timestamp()),
    )
    assert get_timestamp_range("month", "2022-01") == result


def test_year_timestamp():
    result = (
        "de l'année 2021",
        int(datetime(2021, 1, 1, 2, 00).timestamp()),
        int(datetime(2022, 1, 1, 2, 00).timestamp()),
    )
    assert get_timestamp_range("year", "2021") == result
