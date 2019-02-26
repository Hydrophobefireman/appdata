import json
from secrets import token_urlsafe
from typing import Optional

from flask import render_template, request, Response

import constants
from app_data import app
from tables import RequestParser
from utils import jsonify, redirect, send_file


request_parser: RequestParser = RequestParser()


@app.route("/")
def index_page():
    # TODO Dashboard?
    # probably gonna make it a SPA
    return render_template("index.html")


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


@app.route("/get-data/", methods=constants.SUPPORTED_METHODS)
def get_data():
    # data: dict = request.form
    # origin: dict = data.get("$origin")
    # password: str = data.get("pass")
    # site_id: str = data.get("site_id")
    # ret = {
    #     "$or"
    # "db_action": constants.DB_ACTION_READ_TYPE,
    #     "password": password,
    #     "site_id": site_id,
    # }
    data = request.get_json()
    data["transaction_type"] = constants.DATA_MANAGE_TRANSACTION_TYPE
    return jsonify(request_parser.parse_request(data))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
