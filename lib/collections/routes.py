from .views import collections

"""
Sets the mapping between `url_endpoints` and `view functions`.
"""

routes = [
    ("/collections/<id>", {'view_func': collections['index'], 'methods': ["GET", "POST", "PUT", "DELETE"]}),
    ("/collections", {'view_func': collections['index'], 'methods': ["GET", "POST"], 'defaults':{'id': None}}),
    ("/collections/<id>/capabilities", {'view_func': collections['capabilities'], 'methods': ["GET"]}),
    ("/collections/<id>/ops/findMatch", {'view_func': collections['findmatch'], 'methods': ["POST"]}),
    ("/collections/<id>/ops/intersection/<other_id>", {'view_func': collections['intersection'], 'methods': ["GET"]}),
    ("/collections/<id>/ops/union/<other_id>", {'view_func': collections['union'], 'methods': ["GET"]}),
    ("/collections/<id>/ops/flatten", {'view_func': collections['flatten'], 'methods': ["GET"]}),
]
