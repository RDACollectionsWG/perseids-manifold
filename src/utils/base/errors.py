from flask import jsonify


class ModelError(Exception):

    def __init__(self, payload=None):
        Exception.__init__(self)
        self.message = "Invalid Input. The collection properties were malformed or invalid."
        self.status_code = 400
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class ParseError(Exception):

    def __init__(self, payload=None):
        Exception.__init__(self)
        self.message = "Invalid Input. The collection properties were malformed or invalid."
        self.status_code = 400
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class UnauthorizedError(Exception):

    def __init__(self, payload=None):
        Exception.__init__(self)
        self.message = "Unauthorized. Request was not authorized."
        self.status_code = 401
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class ForbiddenError(Exception):

    def __init__(self, payload=None):
        Exception.__init__(self)
        self.message = "Forbidden. Request not possible with current access rights."
        self.status_code = 403
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class NotFoundError(Exception):

    def __init__(self, payload=None):
        Exception.__init__(self)
        self.message = "The collection, member or endpoint was not found."
        self.status_code = 404
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class DBError(Exception):

    def __init__(self, payload=None):
        Exception.__init__(self)
        self.message = "The collection, member or endpoint was not found."
        self.status_code = 500
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class ConflictError(Exception):

    def __init__(self, payload=None):
        Exception.__init__(self)
        self.message = "The collection, member or endpoint was not found."
        self.status_code = 409
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def activate(app):
    @app.errorhandler(ParseError)
    def handle_parse_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response


    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response


    @app.errorhandler(ForbiddenError)
    def handle_forbidden_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response


    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(DBError)
    def handler_db_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(ConflictError)
    def handler_db_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
