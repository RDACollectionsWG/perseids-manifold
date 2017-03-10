from flask import request, json, current_app, redirect
from flask.views import MethodView
from src.collections.models import CollectionResultSet, CollectionObject
from ..utils.errors import *


class CollectionsView(MethodView):
    def get(self, id:None):
        if id:
            try:
                model_type = request.args.get("modelType")
                member_type = request.args.get("memberType")
                ownership = request.args.get("ownership")
                return jsonify(CollectionResultSet(current_app.db.get_collection(id))), 200
            except KeyError:
                raise NotFoundError()
            except FileNotFoundError:
                raise NotFoundError()
            except:
                raise ParseError()
        else:
            try:
                return jsonify(CollectionResultSet(current_app.db.get_collection())), 200
            except:
                raise ParseError()

    def post(self, id:None):
        if not id:
            try:
                id = current_app.db.get_id(CollectionObject)
                current_app.db.set_collection(CollectionObject(id=id, **json.loads(request.data)))
                return jsonify(current_app.db.get_collection(id)[0]), 201
            except PermissionError:
                raise UnauthorizedError()  # 401
            except:
                raise ParseError()  # 400
        else:
            raise NotFoundError()  # 404

    def put(self, id:None):
        if id:
            try:
                c_obj = json.loads(request.data)
                if c_obj.id != id:
                    raise ParseError()
                current_app.db.get_collection(id)
                return jsonify(current_app.db.set_collection(c_obj)), 200
            except (KeyError, FileNotFoundError):
                raise NotFoundError()  # 404
            except UnauthorizedError:
                raise UnauthorizedError()  # 401
            except ForbiddenError:
                raise ForbiddenError()  # 403
            except:
                raise ParseError()  # 400
        else:
            raise NotFoundError()

    def delete(self, id:None):
        if id:
            try:
                current_app.db.del_collection(id)
                return jsonify(''), 200
            except KeyError:
                raise NotFoundError()
            except FileNotFoundError:
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
                cursor = request.args.get("cursor")
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
                cursor = request.args.get("cursor")
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
                cursor = request.args.get("cursor")
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

class RedirectView(MethodView):

    def get(self, id:None):
        return redirect(request.url[:-1], code=307)

    def post(self, id:None):
        return redirect(request.url[:-1], code=307)


collections = {
    'redirect': RedirectView.as_view('redirect'),
    'index': CollectionsView.as_view('collections'),
    'capabilities': CapabilitiesView.as_view('capabilities'),
    'findmatch': FindMatchView.as_view('findmatch'),
    'intersection': IntersectionView.as_view('intersection'),
    'union': UnionView.as_view('union'),
    'flatten': FlattenView.as_view('flatten')
}
