import json
import time
from secrets import token_urlsafe
from typing import Optional

import passlib.hash as pwhash
from flask import Response
from flask import redirect as _redirect
from flask import send_from_directory as _send_from_directory
from urllib.parse import quote as _quote, urlparse
import constants


def jsonify(
    data: dict, code: Optional[int] = 200, headers: Optional[dict] = None
) -> Response:
    """jsonify but only takes a dict, headers, and a response code"""
    return Response(
        json.dumps(data),
        status=code,
        headers=headers,
        content_type=constants.JSON_CONTENT_TYPE,
    )


def redirect(location: str, code: int = 302) -> Response:
    """flask's redirect but always passes the Response class"""
    return _redirect(location, code, Response)


send_file = lambda filename, _dir="static": _send_from_directory(_dir, filename)
"""Shorthand for flasks send_from_directory"""

gen_site_id = lambda m=15: token_urlsafe(m)
"""generate random string for site IDs"""

is_defined = lambda k, scope=locals: k in scope()
"""returns a bool to check if a variable  is defined in the given scope"""


def c_print_as_str(s: str, col: str) -> str:
    _map = {
        "HEADER": "\u001b[95m",
        "OKBLUE": "\u001b[94m",
        "OKGREEN": "\u001b[92m",
        "WARNING": "\u001b[93m",
        "FAIL": "\u001b[91m",
        "BOLD": "\u001b[1m",
        "UNDERLINE": "\u001b[4m",
    }
    _ENDC = "\u001b[0m"
    _ = _map.get(col.upper())
    return f"{_}{s}{_ENDC}"


def c_print(s: str, c: str) -> None:
    return print(c_print_as_str(s, c))


def check_password_hash(_hash: str, pw: str) -> bool:
    meth = pwhash.pbkdf2_sha512
    return meth.verify(pw, _hash)


def hash_password(pw: str) -> str:
    meth = pwhash.pbkdf2_sha512
    return meth.hash(pw)


now = lambda: time.time()
quote = lambda x: _quote(x, safe="")

get_site_host = lambda x: urlparse(x).netloc

