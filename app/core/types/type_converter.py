import json
import logging
import math

from dateutil import parser as date_parser
from pytz import timezone

log = logging.getLogger(__name__)


def bool_val(val, fallback=False):  # FIXME
    if val is None:
        return fallback
    if type(val) is str:
        if str.lower(val) in ["true", '1', '1.0', 't']:
            return True
        elif str.lower(val) in ["null", 'nan', 'false', '0', '-1', '-1.0', 'f', '']:
            return False
        else:
            return fallback
    if type(val) is bool:
        return val
    if type(val) is int:
        return int(val) > 0
    if type(val) is float:
        return float(val) > 0

    return fallback


def datetime_val(val, fallback=None):
    if not val:
        return fallback
    # offset of zero "Z" not supported python
    if val.endswith('Z') or val.endswith('z'):
        val = val[:-1]
    if str.isdecimal(val.lstrip("-")):
        return None
    try:
        datetime = date_parser.parse(val)
    except ValueError:
        log.debug("Failed to parse datetime {}, returning fallback {}", val, fallback)
        return fallback
    if datetime.tzinfo is None:
        log.debug("No timezone on date, setting it to UTC")
        datetime.replace(tzinfo=timezone('UTC'))
    return datetime


def date_val(val, fallback=None):
    if not val:
        return fallback
    # offset of zero "Z" not supported python
    if val.endswith('Z') or val.endswith('z'):
        val = val[:-1]
    if str.isdecimal(val.lstrip("-")):
        return None
    try:
        date = date_parser.parse(val)
        return date.replace(hour=0, minute=0, second=0, microsecond=0)
    except ValueError:
        log.debug("Failed to parse datetime {}, returning fallback {}", val, fallback)
        return fallback


def string_val(val, fallback=None):
    if val is None:
        return fallback
    if type(val) is int or type(val) is float or type(val) is bool:
        return str(val)
    if type(val) is str and val.lower() == 'nan':
        return fallback
    if val.replace(" ", "") == "":
        return fallback
    if str.lower(val) == "null":
        return fallback
    else:
        return val


def float_val(val, fallback=0.0):
    if not val:
        return fallback
    elif type(val) == bool:
        if val == False:
            return -1.0
        return 1.0
    # check what is the string
    if type(val) is str:
        val = val.replace(',', '.')
        if val.lower() == 'nan':
            return float(0)
        elif val.isdigit():
            return float(val)
        elif isfloat(val):
            return float(val)
        else:
            log.warning("Cannot convert '{}' to float, returning fallback {}".format(val, fallback))
            return fallback
    return val


def integer_val(val, fallback=0):
    if val is None:
        return fallback
    if isfloat(val):
        if type(val) is str and val.lower() == 'nan':
            return fallback
        return int(math.floor(float(val)))
    if str.isdigit(val):
        return int(val)
    return fallback


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def json_val(val, fallback=None):
    if val is None:
        return fallback
    if len(val) < 2:  # deals with random single characters such as commas
        return fallback
    try:
        return json.loads(val)
    except json.decoder.JSONDecodeError:
        log.warning("Failed to parse json {}, returning fallback".format(val))
    return fallback


def bool_csv(row, column, fallback):
    return bool_val(safe_csv_val(row, column), fallback=fallback)


def datetime_csv(row, column, fallback):
    return datetime_val(safe_csv_val(row, column), fallback=fallback)


def date_csv(row, column, fallback):
    return date_val(safe_csv_val(row, column), fallback=fallback)


def string_csv(row, column, fallback):
    return string_val(safe_csv_val(row, column), fallback=fallback)


def float_csv(row, column, fallback):
    return float_val(safe_csv_val(row, column), fallback=fallback)


def int_csv(row, column, fallback):
    return integer_val(safe_csv_val(row, column), fallback=fallback)


def json_csv(row, column, fallback):
    return json_val(safe_csv_val(row, column), fallback=fallback)


def safe_csv_val(row, column):
    try:
        if row[column] is None:
            val = row[column]
        else:
            val = row[column].strip()
        if val is None:
            return None
        return val
    except KeyError as err:
        log.info("Failed to fetch {} value from row ".format(column))
        return None
