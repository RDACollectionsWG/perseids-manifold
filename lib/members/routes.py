from .views import members

"""
Sets the mapping between `url_endpoints` and `view functions`.
"""

routes = [
    ("/collections/<id>/members/<mid>", {'view_func': members['members'], 'methods': ["GET", "PUT", "DELETE"]}),
    ("/collections/<id>/members", {'view_func': members['members'], 'methods': ["GET", "POST"], 'defaults':{'mid': None}}),
    ("/collections/<id>/members/<mid>/properties/<property>", {'view_func': members['properties'], 'methods': ["GET", "PUT", "DELETE"]})
]
