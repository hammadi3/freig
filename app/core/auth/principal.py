import boto3
import logging


from flask_cognito import CognitoAuthError

from app.settings import cognito_userpool_id
from app.core.errors import ValidationError

log = logging.getLogger(__name__)

ADMIN_GROUP = 'fd-admin'
GROUPS_KEY = 'cognito:groups'


class Principal:
    """
    A user in the system, governed by attributes and group membership in the cognito jwt token
    Membership of group 'fd-admin' indicates admin privileges, otherwise the first other
    group membership found is the partner_id. Email and Name will be present if the JWT token is of type IdToken.
    If just an AccessToken is provided then the email and name are not accessible (AccessToken is subset of between IdToken)
    """

    def __init__(self, jwt=None, partner_id=None, name=None, email=None, admin=False, username=None):
        if jwt is None:
            self._partner_id = partner_id
            self._name = name
            self._email = email
            self._admin = admin
            self._username = username
        else:
            self._jwt = jwt
            if 'email' in jwt:
                self._email = jwt['email']
            else:
                self._email = None
            if 'name' in jwt:
                self._name = jwt['name']
            else:
                self._name = None
            if 'username' in jwt:
                self._username = jwt['username']
            else:
                self._username = None
            if 'sub' in jwt:
                self._sub = jwt['sub']
            else:
                self._sub = None
            if GROUPS_KEY in jwt:
                groups = jwt[GROUPS_KEY]
                if len(groups) == 0:
                    raise ValidationError('Invalid jwt, no group membership could be determined')
                if ADMIN_GROUP in groups:
                    self._admin = True
                else:
                    self._admin = False
                if len(groups) == 1:
                    self._partner_id = groups[0]
                else:  # in case we have an fd-admin associated with a partner group
                    if ADMIN_GROUP in groups:
                        groups.remove(ADMIN_GROUP)
                    self._partner_id = groups[0]  # don't allow more than one partner id
            else:
                raise ValidationError('Invalid jwt, no group membership could be determined')

    def fetch_cognito_user_attributes(self):
        client = boto3.client("cognito-idp")
        try:
            response = client.admin_get_user(UserPoolId=cognito_userpool_id, Username=self.sub())
        except Exception as e:
            log.exception("Failed to fetch_cognito_user_attributes, error.profile.fetch, AWS Exception:  {}".format(e))
            raise ValidationError("error.fetch_user_attributes.failed")

        for attribute in response['UserAttributes']:
            if attribute['Name'].startswith('custom:'):
                setattr(self, "_"+attribute['Name'][7:], attribute['Value'])
            else:
                setattr(self, "_"+attribute['Name'], attribute['Value'])

    def update_cognito_user_attributes(self, attribute_dictionary):
        custom_attributes = ["partner_id", "language", 'camp_notice_period']
        attribute_list = []
        for key, value in attribute_dictionary.items():
            if value is not None:
                if key not in custom_attributes:
                    attribute_list.append({'Name': key, 'Value': value})
                else:
                    attribute_list.append({'Name': "custom:"+key, 'Value': value})

        if len(attribute_list) == 0:
            raise ValidationError("error.update_user_attributes.failed")

        client = boto3.client("cognito-idp")

        try:
            client.admin_update_user_attributes(UserPoolId=cognito_userpool_id, Username=self.sub(),
                                                UserAttributes=attribute_list)
        except Exception as e:
            log.exception("Failed to update_cognito_user_attributes, error.profile.update, AWS Exception:  {}".format(e))
            raise ValidationError("error.update_user_attributes.failed")

    def partner_id(self):
        return self._partner_id

    def is_admin(self):
        return self._admin

    def email(self):
        return self._email

    def name(self):
        return self._name

    def username(self):
        return self._username

    def sub(self):
        return self._sub
