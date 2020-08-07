import os
import logging


from flask_script import Manager  # class for handling a set of commands
from flask_migrate import Migrate, MigrateCommand, upgrade as _upgrade
from app.db import db, health, clear_database
from app.app import app
from app.settings import db_port, db_host, db_name, db_password, db_user

# notice here you MUST import every new model so alembic can't detect changes
# (linter shows unsed import DON'T Delete it)
from app.model import freigabe, matstamm


log = logging.getLogger('app.db.manage')


migrate = Migrate(app, db)
manager = Manager(app)


@manager.command
def create_db():
    try:
        sql_command = """CREATE DATABASE "{}" WITH OWNER "{}" ENCODING 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';""".format(
            db_name, db_user
        )

        os.system("PGPASSWORD={} psql -p{} -h{} -U {} -d postgres -c \"{}\"".format(
            db_password, db_port, db_host, db_user, sql_command
        ))
        log.debug("Executed create database command")
    except Exception as ex:
        log.exception("Failed to create a new database user", exc_info=True)
        log.exception(ex.msg, exc_info=True)


@manager.command
def drop_db():
    try:
        os.system("PGPASSWORD={} psql -p{} -h{} -U {} -d postgres -c \"DROP DATABASE IF EXISTS {}\"".format(
            db_password, db_port, db_host, db_user, db_name
        ))
        log.debug("Executed Drop database command")
    except Exception as ex:
        log.exception("Failed to drop the database", exc_info=True)
        log.exception(ex, exc_info=True)


@manager.command
def check_health():
    res = health()
    if res[0]:
        log.debug("DB is ok.")


@manager.command
def clear_db():
    clear_database()


manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
