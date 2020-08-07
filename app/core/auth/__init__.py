from botocore.exceptions import ClientError
from app.settings import AWS_REGIOM, cognito_userpool_id, cognito_app_client_id
import logging

import boto3
from flask_cognito import CognitoAuthError
from warrant import Cognito
from warrant.aws_srp import AWSSRP
from app.core.errors import ValidationError


log = logging.getLogger(__name__)


def authenticate(username, password):
    """
    Be careful about using this function excessively, e.g via tests, as the cognito request may get throttled by IP Address
    """
    if not username:
        raise CognitoAuthError("Empty username", "error.auth.invalid_user")
    if not password:
        raise CognitoAuthError("Empty password", "error.auth.invalid_password")

    client = boto3.client('cognito-idp', region_name=AWS_REGIOM)
    log.info("Authenticating user: {}".format(username))
    cognito = AWSSRP(username=username, password=password,
                     pool_id=cognito_userpool_id, client_id=cognito_app_client_id,
                     client=client)
    try:
        tokens = cognito.authenticate_user()
        return {
            'IdToken': tokens['AuthenticationResult']['IdToken'],
            'AccessToken': tokens['AuthenticationResult']['AccessToken'],
            'ExpiresIn': tokens['AuthenticationResult']['ExpiresIn'],
            'RefreshToken': tokens['AuthenticationResult']['RefreshToken'],
            'TokenType': tokens['AuthenticationResult']['TokenType']
        }
    except client.exceptions.NotAuthorizedException as ex:
        log.info("Failed to authenticate user: {}".format(username))
        raise CognitoAuthError(ex, "error.auth.not_authorized")
    except client.exceptions.UserNotFoundException as ex:
        log.info("Invalid user: {}".format(username))
        raise CognitoAuthError(ex, "error.auth.invalid_user")
    except client.exceptions.UserNotConfirmedException as ex:
        log.info("UserNotConfirmedException: {}".format(username))
        raise CognitoAuthError(ex, "error.auth.unconfirmed_user")


def refresh_token(token):
    """
    Be careful about using this function excessively, e.g via tests, as the cognito request may get throttled by IP Address
    """
    client = boto3.client('cognito-idp', region_name=AWS_REGIOM)
    log.info("Refreshing token")
    try:
        tokens = client.initiate_auth(
            ClientId=cognito_app_client_id,
            AuthFlow='REFRESH_TOKEN',
            AuthParameters={'REFRESH_TOKEN': token},
        )
        return {
            'IdToken': tokens['AuthenticationResult']['IdToken'],
            'AccessToken': tokens['AuthenticationResult']['AccessToken'],
            'TokenType': tokens['AuthenticationResult']['TokenType']
        }
    except client.exceptions.NotAuthorizedException as ex:
        log.info("Failed to refresh token user: {}".format(token))
        raise CognitoAuthError(ex, "error.auth.not_authorized")


def verify_aws_credentials():
    """
    Verify connectivity to AWS
    """
    try:
        account_id = boto3.client('sts', region_name=AWS_REGIOM).get_caller_identity()["Account"]
        log.info("Verified AWS credentials {}".format(account_id))
        return account_id
    except Exception as e:
        log.warning("AWS credentials verification failure: {}".format(repr(e)))
    return None


def create_user(username, password, name, group):
    """
    Create user and add him to the specifed group
    """
    if not username:
        raise ValidationError("error.create_user.invalid_user")
    if not password:
        raise ValidationError("error.create_user.invalid_password")
    if not name:
        raise ValidationError("error.create_user.invalid_name")
    if not group:
        raise ValidationError("error.create_user.invalid_group")

    client = boto3.client("cognito-idp")

    # check if group exists or through exception
    try:
        client.get_group(UserPoolId=cognito_userpool_id, GroupName=group)
    except Exception as e:
        log.exception("Failed to get_group, error.create_user.invalid_group, AWS Exception:  {}".format(e))
        raise ValidationError("error.create_user.invalid_group")

    # here I am using warrant library because I found it easier than boto3
    cognito = Cognito(cognito_userpool_id, cognito_app_client_id)
    cognito.add_base_attributes(name=name)
    # Register the user using warrant
    try:
        register_res = cognito.register(username, password)
    except ClientError as e:
        if "Username should be an email." in e.response["Error"]['Message']:
            raise ValidationError("error.create_user.invalid_user")
        elif "An account with the given email already exists." in e.response["Error"]['Message']:
            raise ValidationError("error.create_user.already_exists")
        elif "Password did not conform with policy" in e.response["Error"]['Message']:
            raise ValidationError("error.create_user.invalid_password")
        else:
            log.exception("Failed to register a user, error.create_user.failed, AWS Exception:  {}".format(e))
            raise ValidationError("error.create_user.failed")

    # add user to the group using boto3 library
    try:
        client.admin_add_user_to_group(UserPoolId=cognito_userpool_id, Username=username, GroupName=group)
    except Exception as e:
        log.exception("Failed to add to a group, error.create_user.addtogroup.failed, AWS Exception:  {}".format(e))
        raise ValidationError("error.create_user.addtogroup.failed")

    return register_res


def confirm_user(username, con_code):

    if not username:
        raise ValidationError("error.confirm_user.invalid_username")
    if not con_code:
        raise ValidationError("error.confirm_user.invalid_confirmation_code")

    # here I am using warrant library because I found it easier than boto3
    cognito = Cognito(cognito_userpool_id, cognito_app_client_id)
    try:
        cognito.confirm_sign_up(confirmation_code=con_code, username=username)
    except Exception as e:
        raise ValidationError("error.confirm_user.failed")


def initiate_forgot_password(username):

    if not username:
        raise ValidationError("error.initiate_forgot_password.invalid_username")

    user_cognito = Cognito(cognito_userpool_id, cognito_app_client_id, username=username)

    try:
        user_cognito.initiate_forgot_password()
    except Exception as e:
        raise ValidationError("error.initiate_forgot_password.invalid_username")


def confirm_forgot_password(username, confirmation_code, new_password):

    if not username:
        raise ValidationError("error.confirm_forgot_password.invalid_user")
    if not confirmation_code:
        raise ValidationError("error.confirm_forgot_password.invalid_confirmation_code")
    if not new_password:
        raise ValidationError("error.confirm_forgot_password.invalid_new_password")

    user_cognito = Cognito(cognito_userpool_id, cognito_app_client_id, username=username)

    try:
        user_cognito.confirm_forgot_password(confirmation_code, new_password)
    except Exception as e:
        if "Password does not conform to policy" in str(e):
            raise ValidationError("error.confirm_forgot_password.invalid_new_password")
        else:
            raise ValidationError("error.confirm_forgot_password.failed")
