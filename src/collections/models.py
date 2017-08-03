from random import randint

from src.utils.base.errors import ModelError
from src.utils.base.models import Model


class CollectionResultSet(Model):
    def __init__(self, contents, nextCursor=None, prevCursor=None):
        self.contents = contents
        if nextCursor:
            self.nextCursor = nextCursor
        if prevCursor:
            self.prevCursor = prevCursor


class CollectionObject(Model):
    def __init__(self, id=None, capabilities=None, properties=None, description=None):
        if any(x is None for x in [id, capabilities, properties]):
            raise ModelError()
        self.id = id or 'http://example.org/mem/'+str(randint(100000, 999999)) # todo: make parsing safe and id minting formalized, e.g. give Service Object a function
        self.capabilities = capabilities if isinstance(capabilities, CollectionCapabilities) else CollectionCapabilities(**capabilities)
        self.properties = properties if isinstance(properties, CollectionProperties) else CollectionProperties(**properties)
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
        if any(map(lambda x: x is None, [ownership, license, modelType, hasAccessRestrictions, descriptionOntology])):
            raise ModelError()
        self.ownership = ownership
        self.license = license
        self.modelType = modelType
        self.hasAccessRestrictions = hasAccessRestrictions
        self.descriptionOntology = descriptionOntology
        self.memberOf = []
        if memberOf is not None:
            self.memberOf = sorted(memberOf)



classList = [CollectionObject, CollectionCapabilities, CollectionProperties]
