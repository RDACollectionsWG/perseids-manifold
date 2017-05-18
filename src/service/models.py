from enum import Enum

from src.utils.base.errors import ModelError
from src.utils.base.models import Model


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
                 supportedCollectionOperations=None,
                 supportedModelTypes=None):
        if any(map(lambda x: x is None, [
            providesCollectionPids,
            enforcesAccess,
            supportsPagination,
            asynchronousActions,
            ruleBasedGeneration,
            maxExpansionDepth,
            providesVersioning
        ])):
            print()
            print("PID ", providesCollectionPids)
            print("enf ", enforcesAccess)
            print("supp ", supportsPagination)
            print("asyn", asynchronousActions)
            print("rule ", ruleBasedGeneration)
            print("max ", maxExpansionDepth)
            print("pro ", providesVersioning)
            raise ModelError()
        self.providesCollectionPids = providesCollectionPids
        self.collectionPidProviderType = collectionPidProviderType
        self.enforcesAccess = enforcesAccess
        self.supportsPagination = supportsPagination
        self.asynchronousActions = asynchronousActions
        self.ruleBasedGeneration = ruleBasedGeneration
        self.maxExpansionDepth = maxExpansionDepth
        self.providesVersioning = providesVersioning
        self.supportedCollectionOperations = [] if not supportedCollectionOperations else sorted(supportedCollectionOperations)
        self.supportedModelTypes = [] if not supportedModelTypes else sorted(supportedModelTypes)


classList = [Service]
