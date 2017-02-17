from ..collections.models import *
from ..members.models import *
from ..service.models import *
from json import load
from os import listdir
from os.path import abspath, isdir, join


class DataBase:

    def __init__(self, d_data='data', d_collection='_collection.json'):
        self.d_data = d_data
        self.d_collection = d_collection

    def __load_json__(self, filename):
        with open(filename) as filecontent:
            return load(filecontent)

    def getCollections(self, cid):
        if not cid:
            return self.getCollections([d for d in listdir(self.d_data) if isdir(join(self.d_data, d))])
        else:
            if not type(cid) in (type([]), type(()), type(set())):
                cid = [cid]
            return [self.__load_json__(join(self.d_data, id, self.d_collection)) for id in cid]

    def getMembers(self, cid, mid):
        assert cid
        if not mid:
            return self.getMembers(cid, [m for m in listdir(join(self.d_data, cid)) if m.endswith('.json') and m is not self.d_collection])
        else:
            if not type(mid) in (type([]), type(()), type(set())):
                mid = [mid]
            return [self.__load_json__(join(self.d_data, cid, id)) for id in mid]

    def getService(self):
        return ''





cites = {
    'urn:cite:test_collections.1': CollectionObject(
        "urn:cite:test_collections.1",
        CollectionCapabilities(True, False, False, True, True, "", 5),
        CollectionProperties("perseids:me", "CCbySA", "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md", False, [], "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md"),
        ""
    ),
    'urn:cite:test_collections.2': CollectionObject(
        "urn:cite:test_collections.2",
        CollectionCapabilities(True, False, False, True, True, "", 5),
        CollectionProperties("perseids:me", "CCbySA", "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md", False, [], "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md"),
        ""
    )
}

members = {
    "http://example.org/mem/1": MemberItem("http://example.org/mem/1","http://example.org/loc/1"),
    "http://example.org/mem/2": MemberItem("http://example.org/mem/2","http://example.org/loc/2"),
    "http://example.org/mem/3": MemberItem("http://example.org/mem/3","http://example.org/loc/3"),
    "http://example.org/mem/4": MemberItem("http://example.org/mem/4","http://example.org/loc/4"),
    "http://example.org/mem/5": MemberItem("http://example.org/mem/5","http://example.org/loc/5")
}

service = Service(supported_collections_operations=[Operations.findMatch, Operations.flatten])

dbpath = abspath('./')
