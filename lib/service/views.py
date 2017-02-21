from flask import jsonify, make_response
from flask.views import MethodView
from .models import Service
from ..data.db import db


class FeaturesView(MethodView):
    def get(self):
        return jsonify(db.getService()), 200

features = FeaturesView.as_view('features')
