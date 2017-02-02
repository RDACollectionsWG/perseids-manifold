from flask import request, json
from flask.views import MethodView

from lib.utils.errors import *
from ..data.db import *


class CollectionsView(MethodView):
    def get(self, id:None):
        if id:
            try:
                # todo: rewrite to retrieve collection from data backend
                return jsonify(cites[id]), 200
            except KeyError:
                raise NotFoundError()
            except:
                raise ParseError()
        else:
            try:
                # todo: rewrite to retrieve collection from data backend
                return jsonify(CollectionResultSet(list(cites.values()))), 200
            except:
                raise ParseError()

    def post(self, id:None):
        if not id:
            try:
                # todo: rewrite to retrieve collection from data backend
                return jsonify(json.loads(request.data)), 201
            except PermissionError:
                raise UnauthorizedError()  # 401
            except:
                raise ParseError()  # 400
        else:
            raise NotFoundError()  # 404

    def put(self, id:None):
        if id:
            try:
                # todo: rewrite to retrieve collection from data backend
                return jsonify(json.loads(request.data)), 200
            except KeyError:
                raise NotFoundError()  # 404
            except ParseError:
                raise ParseError()  # 400
            except UnauthorizedError:
                raise UnauthorizedError()  # 401
            except ForbiddenError:
                raise ForbiddenError()  # 403
        else:
            raise NotFoundError()

    def delete(self, id:None):
        if id:
            try:
                # todo: rewrite to retrieve collection from data backend
                return jsonify(), 200
            except KeyError:
                raise NotFoundError()
            except:
                raise UnauthorizedError()
        else:
            raise NotFoundError()


class CapabilitiesView(MethodView):
    def get(self, id):
        if id:
            try:
                # todo: rewrite to retrieve collection from data backend
                return jsonify(cites[id].capabilities), 200
            except KeyError:
                raise NotFoundError()
            except:
                raise UnauthorizedError()
        else:
            raise NotFoundError()


class FindMatchView(MethodView):
    def post(self, id):
        if id:
            try:
                # todo: rewrite to 1. make conversions recursive and 2. get members from collection w/ id
                posted = json.loads(request.data)
                stored = [k.__dict__ for k in members.values()]
                return jsonify(MemberResultSet([m for m in stored if m == posted])), 200
            except KeyError:
                raise NotFoundError()
            except:
                raise UnauthorizedError()
        else:
            raise NotFoundError()



class IntersectionView(MethodView):
    def get(self, id, other_id):
        if id:
            try:
                # todo: 1. make conversions recursive, 2. get members from collection w/ id and 3. compare lists
                posted = [k.__dict__ for k in members.values()]
                stored = [k.__dict__ for k in members.values()]
                return jsonify(MemberResultSet([m for m in stored if m == posted])), 200
            except KeyError:
                raise NotFoundError()
            except:
                raise UnauthorizedError()
        else:
            raise NotFoundError()


class UnionView(MethodView):
    def get(self, id, other_id):
        if id:
            try:
                # todo: 1. make conversions recursive, 2. get members from collection w/ id and 3. compare lists
                posted = [k.__dict__ for k in members.values()]
                stored = [k.__dict__ for k in members.values()]
                return jsonify(MemberResultSet(posted+stored)), 200
            except KeyError:
                raise NotFoundError()
            except:
                raise UnauthorizedError()
        else:
            raise NotFoundError()


class FlattenView(MethodView):
    def get(self, id):
        if id:
            try:
                # todo: 1. make conversions recursive, 2. get members from collection w/ id and 3. compare lists
                posted = [k.__dict__ for k in members.values()]
                stored = [k.__dict__ for k in members.values()]
                return jsonify(MemberResultSet(posted+stored)), 200
            except KeyError:
                raise NotFoundError()
            except:
                raise UnauthorizedError()
        else:
            raise NotFoundError()

collections = {
    'index': CollectionsView.as_view('collections'),
    'capabilities': CapabilitiesView.as_view('capabilities'),
    'findmatch': FindMatchView.as_view('findmatch'),
    'intersection': IntersectionView.as_view('intersection'),
    'union': UnionView.as_view('union'),
    'flatten': FlattenView.as_view('flatten')
}
