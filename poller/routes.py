from flask import Flask, jsonify, request
from datetime import datetime
from time import mktime, strptime

from . import APP
from .models import Day

@APP.route('/api/v0/history')
def _get_api_v0_history():
    after_str = request.args.get("after")
    if after_str == None: 
        return jsonify([day.serialize() for day in Day.get_all()])
    try:
        after = datetime.fromtimestamp(mktime(strptime(after_str, "%Y-%m-%d")))
        return jsonify([day.serialize() for day in Day.get_after(after)])
    except:
        return jsonify({"error": "bad request", "details": "error parsing query 'after'"}), 400


@APP.route('/api/v0/latest')
def _get_api_v0_latest():
    return jsonify(Day.get_all()[-1].serialize())
