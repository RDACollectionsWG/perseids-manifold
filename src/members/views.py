from flask import jsonify, json, request
from flask.json import loads
from flask.views import MethodView
from ..utils.errors import *
from .models import *
from flask import current_app


class MemberView(MethodView):

    def flatten(self, ls):
        return [m for l in ls for m in l]

    def recurse(self, m_obj, depth):
        if depth is 0:
            return [m_obj]
        else:
            try:
                m_objs = current_app.db.get_member(m_obj.id)
                return self.flatten([self.recurse(m, depth-1) for m in m_objs])
            except:
                return [m_obj]


    def get(self, id, mid=None):
        try:
            if mid:
                try:
                    members = current_app.db.get_member(id, mid)
                except UnauthorizedError:
                    raise UnauthorizedError()
            else:
                try:
                    datatype = request.args.get("f_datetype")
                    role = request.args.get("f_role")
                    index = request.args.get("f_index")
                    date_added = request.args.get("f_dateAdded")
                    cursor = request.args.get("cursor")
                    expand_depth = int(request.args.get("expandDepth") or 0)
                    members = current_app.db.get_member(id)
                    if expand_depth is not 0:
                        members = self.flatten([self.recurse(m, expand_depth) for m in members])
                    if datatype:
                        members = [m for m in members if m.datatype == datatype]
                    if role:
                        members = [m for m in members if hasattr(m,'mappings') and m.mappings.role == role]
                    if index:
                        members = [m for m in members if hasattr(m,'mappings') and m.mappings.index == index]
                    if date_added:
                        members = [m for m in members if hasattr(m,'mappings') and m.mappings.dateAdded == date_added]
                except UnauthorizedError:
                    raise UnauthorizedError()
                except:
                    raise ParseError()
        except KeyError:
            raise NotFoundError()
        return jsonify(MemberResultSet(members)), 200

    def post(self, id):
        try:
            posted = json.loads(request.data)
            mid = current_app.db.get_id(MemberItem)
            return jsonify(MemberResultSet([current_app.db.set_member(id, MemberItem(id=mid, **posted))])), 201
        except (KeyError, FileNotFoundError, NotFoundError):
            raise NotFoundError()
        except UnauthorizedError:
            raise UnauthorizedError
        except ForbiddenError:
            raise ForbiddenError()
        except:
            ParseError()

    def put(self, id, mid):
        try:
            posted = json.loads(request.data)
            if posted.id != mid:
                raise ParseError()
            if len(current_app.db.get_member(id, mid)) is not 1:
                raise NotFoundError
            current_app.db.set_member(id, posted)
            return jsonify(MemberResultSet([posted])), 200
        except (KeyError, FileNotFoundError, NotFoundError):
            raise NotFoundError()
        except UnauthorizedError:
            raise UnauthorizedError
        except ForbiddenError:
            raise ForbiddenError()
        except:
            ParseError()  # todo: unexpected error

    def delete(self, id, mid):
        try:
            current_app.db.del_member(id, mid)
            return jsonify(), 200  # todo: use id, mid
        except (KeyError, FileNotFoundError, NotFoundError):
            raise NotFoundError()
        except UnauthorizedError:
            raise UnauthorizedError
        except ForbiddenError:
            raise ForbiddenError()
        except:
            ParseError()


class PropertiesView(MethodView):
    def get(self, id, mid, property):
        try:
            return jsonify(), 200  # todo: use id, mid, property
        except KeyError:
            raise NotFoundError()
        except UnauthorizedError:
            raise UnauthorizedError

    def put(self, id, mid, property):
        try:
            return jsonify(id), 200  # todo: use id, mid, property
        except KeyError:
            raise NotFoundError()
        except UnauthorizedError:
            raise UnauthorizedError
        except ForbiddenError:
            raise ForbiddenError()

    def delete(self, id, mid, property):
        try:
            return jsonify(), 200  # todo: use id, mid, property
        except KeyError:
            raise NotFoundError()
        except UnauthorizedError:
            raise UnauthorizedError
        except ForbiddenError:
            raise ForbiddenError()


members = {
    'members': MemberView.as_view('members'),
    'properties': PropertiesView.as_view('properties'),
}