from flask import jsonify
from flask.views import MethodView
from .models import Service
from ..data.db import service


class FeaturesView(MethodView):
    def get(self):
        return jsonify(service)

features = FeaturesView.as_view('features')
