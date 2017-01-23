from flask import jsonify
from flask.views import MethodView


class FeaturesView(MethodView):
    def get(self):
        return "You ran get on /features"

features = FeaturesView.as_view('features')