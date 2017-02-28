from ..utils.models import Model
from ..utils.errors import ModelError
from random import randint


class CollectionResultSet(Model):
    def __init__(self, contents, nextCursor=None, prevCursor=None):
        self.contents = contents
        if nextCursor:
            self.nextCursor = nextCursor
        if prevCursor:
            self.prevCursor = prevCursor


class CollectionObject(Model):
    def __init__(self, id=None, capabilities=None, properties=None, description=None):
        if any(map(lambda x: x is None, [capabilities, properties])):
            raise ModelError()
        self.id = id or 'http://example.org/mem/'+randint(100000, 999999) # todo: make parsing safe and id minting formalized
        self.capabilities = capabilities
        self.properties = properties
        if description:
            self.description = description


class CollectionCapabilities(Model):
    def __init__(self,
                 isOrdered=None,
                 appendsToEnd=None,
                 supportsRoles=None,
                 membershipIsMutable=None,
                 metadataIsMutable=None,
                 restrictedToType=None,
                 maxLength=None):
        if any(map(lambda x: x is None, [isOrdered,  appendsToEnd, supportsRoles, membershipIsMutable, metadataIsMutable, restrictedToType, maxLength])):
            raise ModelError()
        self.isOrdered = isOrdered
        self.supportsRoles = supportsRoles
        self.appendsToEnd = appendsToEnd
        self.membershipIsMutable = membershipIsMutable
        self.metadataIsMutable = metadataIsMutable
        self.restrictedToType = restrictedToType
        self.maxLength = maxLength


class CollectionProperties(Model):
    def __init__(self,
                 ownership=None,
                 license=None,
                 modelType=None,
                 hasAccessRestrictions=None,
                 memberOf=None,
                 descriptionOntology=None):
        if any(map(lambda x: x is None, [ownership, license, modelType, hasAccessRestrictions, memberOf, descriptionOntology])):
            raise ModelError()
        self.ownership = ownership
        self.license = license
        self.modelType = modelType
        self.hasAccessRestrictions = hasAccessRestrictions
        self.descriptionOntology = descriptionOntology
        if memberOf:
            self.memberOf = memberOf


classList = [CollectionObject, CollectionCapabilities, CollectionProperties]
