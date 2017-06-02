import traceback

from flask import current_app
from flask import json, request
from flask.views import MethodView

from src.utils.base.errors import *
from .models import *


class MemberView(MethodView):

    def flatten(self, ls):
        return [m for l in ls for m in l]

    def recurse(self, m_obj, depth):
        if depth is 0:
            return m_obj
        else:
            try:
                m_objs = current_app.db.get_member(m_obj.id)
                return MemberResultSet([self.recurse(m, depth-1) for m in m_objs])
            except:
                return m_obj

    def get(self, id, mid=None):
        try:
            if mid:
                members = current_app.db.get_member(id, mid)
                result = members[0]
            else:
                datatype = request.args.get("f_datetype")
                role = request.args.get("f_role")
                index = request.args.get("f_index")
                date_added = request.args.get("f_dateAdded")
                cursor = request.args.get("cursor")
                expand_depth = int(request.args.get("expandDepth") or 0)
                members = current_app.db.get_member(id)
                if expand_depth is not 0:
                    members = [self.recurse(m, expand_depth) for m in members]
                if datatype:
                    members = [m for m in members if m.datatype == datatype]
                if role:
                    members = [m for m in members if hasattr(m,'mappings') and m.mappings.role == role]
                if index:
                    members = [m for m in members if hasattr(m,'mappings') and m.mappings.index == index]
                if date_added:
                    members = [m for m in members if hasattr(m,'mappings') and m.mappings.dateAdded == date_added]
                result = MemberResultSet(members)
            return jsonify(result), 200
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()

    def post(self, id):
        try:
            if not id:
                raise NotFoundError()
            obj = json.loads(request.data)
            #if not isinstance(obj, Model):
            #    if current_app.db.get_service().providesCollectionPids:
            #        obj += {'id': current_app.db.get_id(MemberItem)}
            #        obj = MemberItem(**obj)
            try:
                current_app.db.get_member(id, obj.id)
                raise ConflictError()
            except NotFoundError:
                pass
            current_app.db.set_member(id, obj)
            return jsonify(current_app.db.get_member(id, obj.id)), 201
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()

    def put(self, id, mid):
        try:
            posted = json.loads(request.data)
            if posted.id != mid:
                raise ParseError()
            if len(current_app.db.get_member(id, mid)) is not 1:
                raise NotFoundError()
            current_app.db.set_member(id, posted)
            return jsonify(MemberResultSet([posted])), 200
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()

    def delete(self, id, mid):
        try:
            current_app.db.del_member(id, mid)
            return jsonify(), 200  # todo: use id, mid
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()


class PropertiesView(MethodView):

    def write(self, cur, keys, value, create=False):
        if len(keys) == 1:
            cur[keys[0]] = value
            return
        if create and not cur.has_key(keys[0]):
            cur[keys[0]] = {}
        self.write(cur[keys[0]], keys[1:], value)

    def get(self, id, mid, property):
        try:
            result = current_app.db.get_member(id,mid).dict()
            for key in property.split('.'):
                result = result[key]
            return jsonify(result), 200
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()

    def put(self, id, mid, property):
        try:
            posted = json.loads(request.data)['content']
            m_dict = current_app.db.get_member(id,mid).dict()
            self.write(m_dict, property.split("."), posted)
            if m_dict.get('mappings') and not isinstance(m_dict['mappings'], Model):
                m_dict['mappings'] = CollectionItemMappingMetadata(**m_dict['mappings'])
            return jsonify(current_app.db.set_member(MemberItem(**m_dict))), 200
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()

    def delete(self, id, mid, property):
        try:
            return jsonify(), 200  # todo: use id, mid, property
        except (NotFoundError, DBError, UnauthorizedError):
            raise
        except:
            raise ParseError()


members = {
    'members': MemberView.as_view('members'),
    'properties': PropertiesView.as_view('properties'),
}