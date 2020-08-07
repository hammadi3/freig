import os

from flask import Blueprint
from flask import url_for
from flask_restplus import Api
from app.settings import app_data
from app.api.freigaben import api as freigabe_ns
from app.api.matstaemme import api as matstaemme_ns

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}

blueprint = Blueprint('api', __name__)

if os.environ.get('SSL_ENABLED'):
    @property
    def specs_url(self):
        return url_for(self.endpoint('specs'), _external=True, _scheme='https')

    Api.specs_url = specs_url

api = Api(blueprint, version=app_data['version'], title='FreiDB API', description='Freigabedatenbank OEM Support',
          authorizations=authorizations, security='apiKey')


api.add_namespace(freigabe_ns)
api.add_namespace(matstaemme_ns)
