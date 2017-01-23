from flask import jsonify
from flask.views import MethodView


class MembersView(MethodView):
    def get(self, id, mid:None):
        if mid:
            return 'You called get on /collections/'+str(id)+'/members/'+str(mid)
        else:
            return 'You called get on /collections/'+str(id)+'/members'

    def post(self, id):
        return 'You called post on /collections/'+str(id)+'/members'

    def put(self, id, mid):
        return 'You called put on /collections/'+str(id)+'/members/'+str(mid)

    def delete(self, id, mid):
        return 'You called delete on /collections/'+str(id)+'/members/'+str(mid)


class PropertiesView(MethodView):
    def get(self, id, mid, property):
        return 'You called get on /collections/'+str(id)+'/members/'+str(mid)+'/properties/'+str(property)

    def put(self, id, mid, property):
        return 'You called put on /collections/'+str(id)+'/members/'+str(mid)+'/properties/'+str(property)

    def delete(self, id, mid, property):
        return 'You called delete on /collections/'+str(id)+'/members/'+str(mid)+'/properties/'+str(property)


members = {
    'members': MembersView.as_view('members'),
    'properties': PropertiesView.as_view('properties'),
}