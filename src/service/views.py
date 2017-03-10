from flask import jsonify, make_response
from flask.views import MethodView
from .models import Service
from flask import current_app

class FeaturesView(MethodView):
    def get(self):
        return jsonify(current_app.db.get_service()), 200

features = FeaturesView.as_view('features')
