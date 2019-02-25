from os import environ

from set_env import set_env_vars

set_env_vars()

_locked_keys = [
    "project_id",
    "private_key_id",
    "private_key",
    "client_email",
    "client_id",
    "client_x509_cert_url",
]
_default_creds = {
    "type": "service_account",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
}


def get_creds() -> dict:
    for key in _locked_keys:
        if key == "private_key":
            _default_creds[key] = environ[key].replace("\\n", "\n")
        else:
            _default_creds[key] = environ[key]
    return _default_creds
