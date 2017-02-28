from functools import reduce
from enum import Enum
from ..utils.models import Model
from ..utils.errors import ModelError


class Operations(Enum):
    findMatch = 1
    intersection = 2
    union = 3
    flatten = 4


class Service(Model):
    def __init__(self,
                 providesCollectionPids=None,
                 collectionPidProviderType=None,
                 enforcesAccess=None,
                 supportsPagination=None,
                 asynchronousActions=None,
                 ruleBasedGeneration=None,
                 maxExpansionDepth=None,
                 providesVersioning=None,
                 supportedCollectionsOperations=None,
                 supportedModelTypes=None):
        if any(map(lambda x: x is None, [
            providesCollectionPids,
            enforcesAccess,
            supportsPagination,
            asynchronousActions,
            ruleBasedGeneration,
            maxExpansionDepth,
            providesVersioning,
            supportedCollectionsOperations,
            supportedModelTypes
        ])):
            raise ModelError()
        self.providesCollectionPids = providesCollectionPids
        self.collectionPidProviderType = collectionPidProviderType
        self.enforcesAccess = enforcesAccess
        self.supportsPagination = supportsPagination
        self.asynchronousActions = asynchronousActions
        self.ruleBasedGeneration = ruleBasedGeneration
        self.maxExpansionDepth = maxExpansionDepth
        self.providesVersioning = providesVersioning
        self.supportedCollectionsOperations = [] if not supportedCollectionsOperations else supportedCollectionsOperations
        self.supportedModelTypes = [] if not supportedModelTypes else supportedModelTypes


classList = [Service]
