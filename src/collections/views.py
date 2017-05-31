from flask import request, json, redirect, current_app as app
from flask.views import MethodView
from src.utils.base.models import Model

from src.collections.models import CollectionResultSet, CollectionObject
from src.members.models import MemberResultSet, MemberItem
from src.utils.base.errors import *


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
    def get(self, id=None):
        # todo: pagination
        # todo: maxExp
        try:
            if id:
                if app.service.enforcesAccess and not app.acl.get_permission(app.acl.get_user(),id).r:
                    raise UnauthorizedError()
                collections = app.db.get_collection(id)
                result = collections[0]
            else:
                model_type = request.args.get("f_modelType")
                member_type = request.args.get("f_memberType")
                ownership = request.args.get("f_ownership")
                collections = app.db.get_collection()
                if app.service.enforcesAccess:
                    collections = [c for c in collections if app.acl.get_permission(app.acl.get_user(), c.id).r]
                if model_type:
                    collections = [c for c in collections if c.properties.modelType == model_type]
                if member_type:
                    collections = [c for c in collections if c.capabilities.restrictedToType == member_type]
                if ownership:
                    collections = [c for c in collections if c.properties.ownership == ownership]
                result = CollectionResultSet(collections)
            return jsonify(result), 200
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()  # 400

    def post(self, id=None):
        try:
            if id:
                raise NotFoundError()  # 404
            if app.service.enforcesAccess and not app.acl.get_permission(app.acl.get_user()).x:
                raise UnauthorizedError()
            obj = json.loads(request.data)
            if not isinstance(obj, Model):
                if app.db.get_service().providesCollectionPids:
                    obj += {'id': app.mint.get_id(CollectionObject)}
                    obj = CollectionObject(**obj)
            app.db.set_collection(obj)
            return jsonify(app.db.get_collection(obj.id).pop()), 201
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()  # 400

    def put(self, id=None):
        try:
            if not id:
                raise NotFoundError()
            if app.service.enforcesAccess and not app.acl.get_permission(app.acl.get_user(),id).w:
                raise UnauthorizedError()
            c_obj = json.loads(request.data)
            if c_obj.id != id:
                raise ParseError()
            app.db.get_collection(id)
            return jsonify(app.db.set_collection(c_obj)), 200
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()  # 400

    def delete(self, id=None):
        try:
            if not id:
                raise NotFoundError()
            if app.service.enforcesAccess and not app.acl.get_permission(app.acl.get_user(),id).x:
                raise UnauthorizedError()
            app.db.del_collection(id)
            return jsonify(''), 200
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()  # 400


class CapabilitiesView(MethodView):
    def get(self, id):
        try:
            if not id:
                raise NotFoundError()
            if app.service.enforcesAccess and not app.acl.get_permission(app.acl.get_user(),id).r:
                raise UnauthorizedError()
            return jsonify(app.db.get_collection(id)[0].capabilities), 200
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()  # 400


class FindMatchView(MethodView):
    def post(self, id):
        try:
            if not id:
                raise NotFoundError
            if 'findMatch' not in app.service.supportedCollectionOperations:
                raise NotFoundError()
            if app.service.enforcesAccess and not app.acl.get_permission(app.acl.get_user(),id).r:
                raise UnauthorizedError
            posted = json.loads(request.data)
            if isinstance(posted, Model):
                posted = posted.dict()
            if isinstance(posted.get('mappings'), Model):
                posted['mappings'] = posted.get('mappings').dict()
            members = [m for m in app.db.get_member(id) if dict_subset(posted, m.dict())]
            return jsonify(MemberResultSet(members)), 200
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()  # 400


class IntersectionView(MethodView):
    def get(self, id, other_id):
        try:
            if not (id and other_id):
                raise NotFoundError()
            if 'intersection' not in app.service.supportedCollectionOperations:
                raise NotFoundError()
            if app.service.enforcesAccess and not (app.acl.get_permission(app.acl.get_user(),id).r and app.acl.get_permission(app.acl.get_user(),other_id).r):
                raise UnauthorizedError()
            if (id == other_id):
                intersection =  app.db.get_member(id)
            else:
                set1 = [m.dict() for m in app.db.get_member(id)]
                set2 = [m.dict() for m in app.db.get_member(other_id)]
                intersection = [MemberItem(**m) for m in set1 if m in set2]
            return jsonify(MemberResultSet(intersection)), 200
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()  # 400


class UnionView(MethodView):
    def get(self, id, other_id):
        try:
            if not (id and other_id):
                raise NotFoundError()
            if 'union' not in app.service.supportedCollectionOperations:
                raise NotFoundError()
            if app.service.enforcesAccess and not (app.acl.get_permission(app.acl.get_user(),id).r and app.acl.get_permission(app.acl.get_user(),other_id).r):
                raise UnauthorizedError()
            if (id == other_id):
                union =  app.db.get_member(id)
            else:
                set1 = [m.dict() for m in app.db.get_member(id)]
                set2 = [m.dict() for m in app.db.get_member(other_id)]
                union = set1 + [m for m in set2 if m not in set1]
            return jsonify(MemberResultSet([MemberItem(**m) for m in union])), 200
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()  # 400


class FlattenView(MethodView):

    def flatten(self, ls):
        return [m for l in ls for m in l]

    def recurse(self, m_obj, depth):
        if depth is 0:
            return [m_obj]
        else:
            try:
                m_objs = app.db.get_member(m_obj.id)
                return self.flatten([self.recurse(m, depth-1) for m in m_objs])
            except:
                return [m_obj]

    def get(self, id):
        try:
            if not id:
                raise NotFoundError()
            if 'flatten' not in app.service.supportedCollectionOperations:
                raise NotFoundError()
            members = self.flatten([self.recurse(m, -1) for m in app.db.get_member(id)])
            if app.service.enforcesAccess:
                if not app.acl.get_permission(app.acl.get_user(),id).r:
                    raise UnauthorizedError()
                else:
                    members = [m for m in members if app.acl.get_permission(app.acl.get_user(),id,m.id).r]
            return jsonify(MemberResultSet(members)), 200
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()  # 400


class RedirectView(MethodView):

    def get(self, id=None):
        return redirect(request.url[:-1], code=307)

    def post(self, id=None):
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
