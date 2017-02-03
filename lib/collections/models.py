from ..utils.models import Model


class CollectionResultSet(Model):
    def __init__(self, contents, next_cursor=None, prev_cursor=None):
        self.contents = contents
        if next_cursor:
            self.next_cursor = next_cursor
        if prev_cursor:
            self.prev_cursor = prev_cursor


class CollectionObject(Model):
    def __init__(self, id, capabilities, properties, description=None):
        self.id = id
        self.capabilities = capabilities
        self.properties = properties
        if description:
            self.description = description


class CollectionCapabilities(Model):
    def __init__(self,
                 is_ordered,
                 appends_to_end,
                 supports_roles,
                 membership_is_mutable,
                 metadata_is_mutable,
                 restricted_to_type,
                 max_length):
        self.is_ordered = is_ordered
        self.supports_roles = supports_roles
        self.appends_to_end = appends_to_end
        self.membership_is_mutable = membership_is_mutable
        self.metadata_is_mutable = metadata_is_mutable
        self.restricted_to_type = restricted_to_type
        self.max_length = max_length


class CollectionProperties(Model):
    def __init__(self,
                 ownership,
                 license,
                 model_type,
                 has_access_restrictions,
                 member_of,
                 description_ontology):
        self.ownership = ownership
        self.license = license
        self.model_type = model_type
        self.has_access_restrictions = has_access_restrictions
        self.description_ontology = description_ontology
        if member_of:
            self.member_of = member_of
