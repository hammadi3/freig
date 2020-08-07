import logging
import os

from flask_sqlalchemy import SQLAlchemy

log = logging.getLogger(__name__)
db = SQLAlchemy()


def clear_database():
    try:
        x = execute_sql("DELETE FROM freigabe;")
        log.info(x._saved_cursor.statusmessage)
    except Exception as ex:
        log.exception("Failed to clear_database, CHECK syntax in /data/clear_database.sql")
        raise ex


def get_sql_path(name):
    return os.path.join(os.path.dirname(__file__), "..", ".." "/sql", name)


def execute_sql(sql):
    connection = db.engine.connect()
    transaction = connection.begin()
    result = connection.execute(sql)
    transaction.commit()
    return result


def execute_sql_file(sql_file):
    with open(sql_file, "rb") as f:
        sql = f.read().decode("utf8")
    return execute_sql(sql)


def health():
    log.debug("Checking DB health....")
    try:
        execute_sql("SELECT 1")
        log.debug("db ok")
        return True, "db ok"
    except Exception as ex:
        log.exception("DB is unhealthy", exc_info=True)
        raise ex
