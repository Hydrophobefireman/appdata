from typing import List as _List, Optional as _Optional
from os.path import (
    join as _join
)  # prevent useless imports when doing "from constants import *""

# Update whenever making changes to data.jsu
CURRENT_VERSION: int = 1

# Should stay the same i guess
HOST: str = "ssl-appdata.herokuapp.com"

# Probably just throw in http unless window.isSecureContext in the browser
PREFFERED_PROTO: str = "https"

# Json type is great but i don't like the idea of an options request
JSON_CONTENT_TYPE: str = "application/json"
FORM_CONTENT_TYPE: str = "application/x-www-form-urlencoded"

#  Heroku times websockets out after 1 min of inactivity
SUPPORTS_WEBSOCKET: bool = False

MAIN_ENDPOINT: str = "/api/v1/"

# I could probably get with query string but posts are good for now
SUPPORTED_METHODS: _List[str] = ["POST"]

# navigator.sendBeacon is great..test for the support and use it instead of a json request
# dont support beacon right now
BEACON_SUPPORT: bool = False

BEACON_ENDPOINT: str = "/api/v1/beacons"
BEACON_TEST_URL: str = "/api/_/beacon-test"


SUPPORTED_REQUEST_CONTENT_TYPES: _List[str] = [JSON_CONTENT_TYPE, FORM_CONTENT_TYPE]


SCRIPT_LOCATION: str = f"/data-v{CURRENT_VERSION}.js"

DEFAULT_SCRIPT_LOCATION: str = f"/data.js"

SCRIPT_LOCATION_CDN: _Optional[str] = NotImplemented

SITE_META: str = "siteMeta"

SITE_DATA: str = "siteData"

ACCOUNT_CREATE_TRANSACTION_TYPE = 0
DATA_MANAGE_TRANSACTION_TYPE = 1

DB_ACTION_READ_TYPE = 2
DB_ACTION_WRITE_TYPE = 3

DATA_TO_READ = "$R"
DATA_TO_WRITE = "$W"

ANALYTICS = "ANALYTICS"

ANALYTICS_FIELDS: _List[dict] = [
    {"NAME": "VIEW_COUNT", "EXPECTED_TYPE": None, "SET_BY_SERVER": True},
    {"NAME": "INTERNAL_JSON_CONFIG_DATA", "EXPECTED_TYPE": dict},
    {"NAME": "INDIVIDUAL_VISIT_DATA", "EXPECTED_TYPE": dict},
    {"NAME": "SESSION_STORAGE_DATA", "EXPECTED_TYPE": dict},
    {"NAME": "ACTIONS", "EXPECTED_TYPE": dict},
]
