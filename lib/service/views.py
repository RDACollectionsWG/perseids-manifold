from flask import jsonify, make_response
from flask.views import MethodView
from .models import Service
from ..data.db import service


class FeaturesView(MethodView):
    def get(self):
        return jsonify(service), 200

features = FeaturesView.as_view('features')
