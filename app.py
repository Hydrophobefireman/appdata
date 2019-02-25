import json
from secrets import token_urlsafe
from typing import Optional

from flask import render_template, request, Response
from sqlalchemy.orm.attributes import flag_modified

import constants
from app_data import app
from tables import RequestParser
from utils import jsonify, redirect, send_file


request_parser: RequestParser = RequestParser()
# /api/v1/
@app.route(constants.MAIN_ENDPOINT, methods=constants.SUPPORTED_METHODS)
def main_api():
    headers: dict = request.headers
    data: Optional[dict]
    content_type: str = headers.get("content-type", "").lower()
    if content_type not in constants.SUPPORTED_REQUEST_CONTENT_TYPES:
        return jsonify({"error": "Invalid request content type"}, 400)
    if content_type == constants.JSON_CONTENT_TYPE:
        data = request.get_json()
    else:
        data = request.form
    ret = request_parser.parse_request(data, headers)
    return jsonify(ret)


if constants.BEACON_SUPPORT:

    @app.route(constants.BEACON_ENDPOINT, methods=constants.SUPPORTED_METHODS)
    def beacon_api():
        headers: dict = request.headers
        data: Optional[dict] = request.form
        request_parser.parse_request(data, headers)
        return ""


@app.after_request
def resp_headers(resp):
    resp.headers["access-control-allow-origin"] = request.headers.get("origin", "*")
    resp.headers["Access-Control-Allow-Headers"] = request.headers.get(
        "Access-Control-Request-Headers", "*"
    )
    resp.headers["access-control-allow-credentials"] = "true"
    return resp


if __name__ == "__main__":
    app.run(port=5000, debug=True)
