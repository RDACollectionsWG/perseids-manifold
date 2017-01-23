from .views import features

"""
Sets the mapping between `url_endpoints` and `view functions`.
"""

routes = [
    ("/features", {'view_func': features, 'methods': ["GET"]})
]
