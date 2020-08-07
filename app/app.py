import logging

from flask import Flask, redirect
from flask_migrate import Migrate, MigrateCommand
from flask_migrate import upgrade as _upgrade
from healthcheck import EnvironmentDump, HealthCheck

from app import settings
from app.api import blueprint as api_blueprint
from app.db import db
from app.db import health as db_health

log = logging.getLogger(__package__)


def create_app(test_config=None):
    log.info("Creating python app "+__name__)
    flask_app = Flask(__name__)
    flask_app.config.update(settings.PROPS)

    if test_config is not None:
        flask_app.config.update(test_config)
    flask_app.register_blueprint(api_blueprint, url_prefix='/api')

    if test_config is None:
        if flask_app.config.get("COGNITO_CHECK_TOKEN_EXPIRATION") is False:
            log.warning("COGNITO_CHECK_TOKEN_EXPIRATION is disabled, ensure it is enabled in production environments.")
        if flask_app.config.get("FLASK_DEBUG") is True:
            log.warning("FLASK_DEBUG is enabled, ensure it is disabled in production environments.")

    # db initialization
    try:
        db.init_app(flask_app)
    except Exception as e:
        log.exception("Failed to initialize APP: {}".format(repr(e)), exc_info=True)

    # Migrations (upgrade to the latest version)
    with flask_app.app_context():
        try:
            from flask_migrate import upgrade as _upgrade
            migrate = Migrate(flask_app, db)
            _upgrade()
        except Exception as e:
            log.exception("Failed to upgrade DB: {}".format(repr(e)), exc_info=True)

    health = HealthCheck()
    env_dump = EnvironmentDump(include_python=True,
                               include_os=True,
                               include_process=True)
    health.add_check(db_health)
    application_data = settings.application_data()
    # application_data['verified_aws_credentials'] = verify_aws_credentials()
    log.info(application_data)
    env_dump.add_section("application", application_data)
    env_dump.add_section("features", settings.features())

    # Add a flask route to expose information
    flask_app.add_url_rule("/health", "healthcheck", view_func=lambda: health.run())
    flask_app.add_url_rule("/info", "environment", view_func=lambda: env_dump.run())

    return flask_app


app = create_app()


@app.route('/')
def index():
    return redirect('/api')


@app.after_request
def after_request_func(response):
    response.headers.add('access-control-allow-credentials', 'true')
    response.headers.add('access-control-allow-headers', '*')
    response.headers.add('access-control-allow-methods', 'GET,PUT,POST,DELETE')
    response.headers.add('access-control-allow-origin', '*')
    response.headers.add('access-control-expose-headers', '*')
    response.headers.add('access-control-max-age', '21600')
    return response


if __name__ == "__main__":
    app.run(host=settings.server_host, debug=settings.debug, port=settings.server_port)
