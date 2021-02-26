from flask import Flask, jsonify
from . import APP
from .models import Day

@APP.route('/api/v0/history')
def _get_api_v0_history():
    return jsonify([day.serialize() for day in Day.get_all()])

@APP.route('/api/v0/latest')
def _get_api_v0_latest():
    return jsonify(Day.get_all()[-1].serialize())
