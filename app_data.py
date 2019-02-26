import os

from flask import Flask, Response, render_template

import constants
from set_env import set_env_vars
from utils import redirect, send_file

set_env_vars()
app: Flask = Flask(__name__)
app.secret_key: str = os.environ.get("FLASK-app-secret-key")

@app.route(constants.DEFAULT_SCRIPT_LOCATION)
@app.route("/data-latest.js")
def script_file_latest():
    return redirect(constants.SCRIPT_LOCATION)


@app.route("/data-v<int:script_version>.js")
def script_file(script_version):
    return send_file(f"data-v{script_version}.js")


@app.errorhandler(404)
def handle404(_e):
    return Response(
        "errorcode: 404", headers={"content-type": "text/plain"}, status=404
    )


if __name__ == "__main__":
    app.run()
