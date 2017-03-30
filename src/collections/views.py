from flask import request, json, current_app, redirect
from flask.views import MethodView
from src.collections.models import CollectionResultSet, CollectionObject
from src.members.models import MemberResultSet, MemberItem
from src.utils.errors import *
from src.utils.models import Model

def dict_subset(dict1, dict2):
    for key, value in dict1.items():
        if dict2.get(key) is None:
            return False
        elif isinstance(value, dict):
            if not dict_subset(dict1.get(key), dict2.get(key)):
                return False
        elif dict2.get(key) != value:
            return False
    return True

class CollectionsView(MethodView):
    def get(self, id:None):
        if id:
            try:
                collections = current_app.db.get_collection(id)
            except KeyError:
                raise NotFoundError()
            except FileNotFoundError:
                raise NotFoundError()
            except:
                raise ParseError()
        else:
            try:
                model_type = request.args.get("f_modelType")
                member_type = request.args.get("f_memberType")
                ownership = request.args.get("f_ownership")
                collections = current_app.db.get_collection()
                if model_type:
                    collections = [c for c in collections if c.properties.modelType == model_type]
                if member_type:
                    collections = [c for c in collections if c.capabilities.restrictedToType == member_type]
                if ownership:
                    collections = [c for c in collections if c.properties.ownership == ownership]
            except:
                raise ParseError()
        return jsonify(CollectionResultSet(collections)), 200

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
                return jsonify(current_app.db.get_collection(id)[0].capabilities), 200
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
                posted = json.loads(request.data)
                if isinstance(posted, Model):
                    posted = posted.dict()
                if isinstance(posted.get('mappings'), Model):
                    posted['mappings'] = posted.get('mappings').dict()
                members = [m for m in current_app.db.get_member(id) if dict_subset(posted, m.dict())]
                return jsonify(MemberResultSet(members)), 200
            except KeyError:
                raise NotFoundError()
            except:
                raise UnauthorizedError()
        else:
            raise NotFoundError()


class IntersectionView(MethodView):
    def get(self, id, other_id):
        if id and other_id:
            try:
                if (id == other_id):
                    intersection =  current_app.db.get_member(id)
                else:
                    set1 = [m.dict() for m in current_app.db.get_member(id)]
                    set2 = [m.dict() for m in current_app.db.get_member(other_id)]
                    intersection = [MemberItem(**m) for m in set1 if m in set2]
                return jsonify(MemberResultSet(intersection)), 200
            except KeyError:
                raise NotFoundError()
            except:
                raise UnauthorizedError()
        else:
            raise NotFoundError()


class UnionView(MethodView):
    def get(self, id, other_id):
        if id and other_id:
            try:
                if (id == other_id):
                    union =  current_app.db.get_member(id)
                else:
                    set1 = [m.dict() for m in current_app.db.get_member(id)]
                    set2 = [m.dict() for m in current_app.db.get_member(other_id)]
                    union = set1 + [m for m in set2 if m not in set1]
                return jsonify(MemberResultSet([MemberItem(**m) for m in union])), 200
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
