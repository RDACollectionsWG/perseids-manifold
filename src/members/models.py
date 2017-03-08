from ..utils.models import Model
from ..utils.errors import ModelError
from random import randint


class MemberResultSet(Model):
    def __init__(self, contents=None, nextCursor=None, prevCursor=None):
        assert all(map(lambda r: r is not None, [contents]))
        self.contents = contents
        if nextCursor is not None:
            self.nextCursor = nextCursor
        if prevCursor :
            self.prevCursor = prevCursor


class MemberItem(Model):
    def __init__(self, id=None, location=None, datatype=None, ontology=None, mappings=None):
        assert all(map(lambda r: r is not None, [id, location]))
        self.id = id or 'http://example.org/mem/'+randint(100000, 999999) # todo: make parsing safe and id minting formalized
        self.location = location
        if datatype is not None:
            self.datatype = datatype
        if ontology is not None:
            self.ontology = ontology
        if mappings is not None:
            self.mappings = mappings if type(mappings) is CollectionItemMappingMetadata else CollectionItemMappingMetadata(**mappings)


class CollectionItemMappingMetadata(Model):
    def __init__(self, role=None, index=None, dateAdded=None):
        assert any(map(lambda r: r is not None, [role, index, dateAdded]))
        self.role = role
        self.index = index
        self.dateAdded = dateAdded

classList = [MemberItem, CollectionItemMappingMetadata]
