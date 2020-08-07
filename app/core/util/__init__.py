from datetime import datetime
from datetime import timedelta
from datetime import timezone

from app.core.errors import ValidationError


# 2020-04-01T19:30:00+00:00

def create_weeks(period):
    """
        Values for since
        1w - last week  - timedelta(weeks=1)
        2w - last two weeks  - timedelta(weeks=12)
        4w - last four weeks  - timedelta(weeks=4)
        1m - last month - timedelta(weeks=4)
        1q - last quarter - timedelta(weeks=12)
        1y - last year - timedelta(weeks=52)
        """

    if period is None:
        raise ValidationError("Invalid syntax for 'since': Expected number followed by w|m|q|y ")
    if period.endswith('w'):
        weeks = 1
    elif period.endswith('m'):
        weeks = 4
    elif period.endswith('q'):
        weeks = 12
    elif period.endswith('y'):
        weeks = 52
    else:
        raise ValidationError("Invalid syntax for 'period': Expected number followed by w|m|q|y ")
    return weeks

def get_date_since(since):
    weeks = create_weeks(since)
    number_str = since[:-1]
    if not number_str.isdigit():
        raise ValidationError("Invalid syntax for 'since': Expected number followed by w|m|q|y ")
    total_weeks = weeks * int(number_str)

    return approx_date_time(datetime.now(timezone.utc) - timedelta(weeks=total_weeks))



# 2020-04-01T19:30:00+00:00
def get_date_until(until):
    weeks = create_weeks(until)
    number_str = until[:-1]
    if not number_str.isdigit():
        raise ValidationError("Invalid syntax for 'until': Expected number followed by w|m|q|y ")

    total_weeks = weeks * int(number_str)

    return approx_date_time(datetime.now(timezone.utc) + timedelta(weeks=total_weeks))



def approx_date_time(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
            + timedelta(hours=t.minute // 30))


def now_utc():
    return datetime.now(timezone.utc)
