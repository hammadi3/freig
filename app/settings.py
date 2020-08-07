import datetime
import json
import logging.config
import os


logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__package__)

deployed_since = datetime.datetime.now().isoformat()

db_name = os.getenv("DB_NAME", "freigabe")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "54320")
db_user = os.getenv("DB_USER", "freigabe")
db_password = os.getenv("DB_PASSWORD", "freigabe")
db_uri = 'postgresql://' + db_user + ':' + db_password + '@' + db_host + ':' + db_port + '/' + db_name
server_host = os.getenv("FLASK_RUN_HOST", 'localhost')
server_port = os.getenv("FLASK_RUN_PORT", "5000")
debug = "TRUE"

PROPS = {
    'FLASK_DEBUG': debug,
    'SQLALCHEMY_DATABASE_URI': db_uri,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SWAGGER_UI_DOC_EXPANSION': 'list',
    'RESTPLUS_VALIDATE': True,
    'RESTPLUS_MASK_SWAGGER': False,
    'ERROR_404_HELP': False,
    'COGNITO_REGION': os.getenv('COGNITO_REGION', "eu-central-1")
}


def application_data():
    app_data_file = os.path.normpath(os.path.join(os.path.dirname(__file__), '../version.json'))
    try:
        with open(app_data_file, 'r') as f:
            data = json.load(f)
            data['version'] = ":".join([data['build_number'], deployed_since])
    except Exception:
        return {'version': 'development', 'build_number': 0, 'deployed_since': deployed_since}
    return data


def features():
    # temporary solution and we will not use get_features function from features package
    return {'campaign.simulation': True}


app_data = application_data()
