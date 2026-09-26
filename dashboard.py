"""
Dashboard: bogga webka ah ee tusaya signals-ka ugu dambeeyay.
"""
from flask import Flask, render_template, jsonify

import config
import storage

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/signals")
def api_signals():
    return jsonify(storage.get_recent_signals(limit=50))


@app.route("/healthz")
def healthz():
    """Render (iyo UptimeRobot) waxay isticmaali karaan tan si ay u
    ogaadaan in app-ku uu shaqeeyo."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host=config.DASHBOARD_HOST, port=config.DASHBOARD_PORT, debug=False)
