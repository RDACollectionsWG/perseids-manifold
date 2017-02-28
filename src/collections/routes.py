from .views import collections

"""
Sets the mapping between `url_endpoints` and `view functions`.
"""

routes = [
    ("/collections/<path:id>", {'view_func': collections['index'], 'methods': ["GET", "POST", "PUT", "DELETE"]}),
    ("/collections/", {'view_func': collections['index'], 'methods': ["GET", "POST"], 'defaults':{'id': None}}),
    ("/collections/<path:id>/capabilities", {'view_func': collections['capabilities'], 'methods': ["GET"]}),
    ("/collections/<path:id>/ops/findMatch", {'view_func': collections['findmatch'], 'methods': ["POST"]}),
    ("/collections/<path:id>/ops/intersection/<path:other_id>", {'view_func': collections['intersection'], 'methods': ["GET"]}),
    ("/collections/<path:id>/ops/union/<path:other_id>", {'view_func': collections['union'], 'methods': ["GET"]}),
    ("/collections/<path:id>/ops/flatten", {'view_func': collections['flatten'], 'methods': ["GET"]}),
]
