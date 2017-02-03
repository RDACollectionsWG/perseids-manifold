from ..utils.models import Model

class MemberResultSet(Model):
    def __init__(self, contents, next_cursor=None, prev_cursor=None):
        self.contents = contents
        if next_cursor:
            self.next_cursor = next_cursor
        if prev_cursor:
            self.prev_cursor = prev_cursor


class MemberItem(Model):
    def __init__(self, id, location, datatype=None, ontology=None, mappings=None):
        self.id = id
        self.location = location
        if datatype:
            self.datatype = datatype
        if ontology:
            self.ontology = ontology
        if mappings:
            self.mappings = mappings

class CollectionItemMappingMetadata(Model):
    def __init__(self, role=None, index=None, dateAdded=None):
        self.role = role
        self.index = index
        self.dateAdded = dateAdded

signatures = {
    frozenset('id', 'location','datatype','ontology','mappings'): MemberItem,
    frozenset('role','index','dateAdded'): CollectionItemMappingMetadata
}