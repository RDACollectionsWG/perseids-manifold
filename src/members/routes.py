from .views import members

"""
Sets the mapping between `url_endpoints` and `view functions`.
"""

routes = [
    ("/collections/<path:id>/members/<path:mid>", {'view_func': members['members'], 'methods': ["GET", "PUT", "DELETE"]}),
    ("/collections/<path:id>/members/", {'view_func': members['members'], 'methods': ["GET", "POST"], 'defaults':{'mid': None}}),
    ("/collections/<path:id>/members/<path:mid>/properties/<path:property>", {'view_func': members['properties'], 'methods': ["GET", "PUT", "DELETE"]})
]
