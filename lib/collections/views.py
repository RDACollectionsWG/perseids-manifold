from flask import jsonify
from flask.views import MethodView


class CollectionsView(MethodView):
    def get(self, id:None):
        if id:
            res = ' '+str(id)
        else:
            res = '!'
        return 'You called get on /collections/'+str(id)

    def post(self, id:None):
        if id:
            res = ' '+str(id)
        else:
            res = '!'
        return 'You called post on /collections/'+str(id)

    def put(self, id:None):
        if id:
            res = ' '+str(id)
        else:
            res = '!'
        return 'You called put on /collections/'+str(id)

    def delete(self, id:None):
        if id:
            res = ' '+str(id)
        else:
            res = '!'
        return 'You called delete on /collections/'+str(id)


class CapabilitiesView(MethodView):
    def get(self, id):
        return 'You called get on /collections/'+str(id)+'/capabilities'


class FindMatchView(MethodView):
    def post(self, id):
        return 'You called post on /collections/'+str(id)+'/ops/findMatch'


class IntersectionView(MethodView):
    def get(self, id, other_id):
        return 'You called get on /collections/'+str(id)+'/ops/intersection/'+str(other_id)


class UnionView(MethodView):
    def get(self, id, other_id):
        return 'You called get on /collections/'+str(id)+'/ops/union/'+str(other_id)


class FlattenView(MethodView):
    def get(self, id):
        return 'You called get on /collections/'+str(id)+'/ops/flatten'

collections = {
    'index': CollectionsView.as_view('collections'),
    'capabilities': CapabilitiesView.as_view('capabilities'),
    'findmatch': FindMatchView.as_view('findmatch'),
    'intersection': IntersectionView.as_view('intersection'),
    'union': UnionView.as_view('union'),
    'flatten': FlattenView.as_view('flatten')
}