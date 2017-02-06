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
                 provides_collection_pids=False,
                 collection_pid_provider_type=None,  # todo: optional
                 enforces_access=False,
                 supports_pagination=False,
                 asynchronous_actions=False,
                 rule_based_generation=False,
                 max_expansion_depth=0,
                 provides_versioning=False,
                 supported_collections_operations=None,
                 supported_model_types=None):
        if reduce(lambda x,y: x & y is not None, [
            provides_collection_pids,
            enforces_access,
            supports_pagination,
            asynchronous_actions,
            rule_based_generation,
            max_expansion_depth,
            provides_versioning,
            supported_collections_operations,
            supported_model_types
        ]):
            raise \
                ModelError()
        self.provides_collection_pids = provides_collection_pids
        self.collection_pid_provider_type = collection_pid_provider_type
        self.enforces_access = enforces_access
        self.supports_pagination = supports_pagination
        self.asynchronous_actions = asynchronous_actions
        self.rule_based_generation = rule_based_generation
        self.max_expansion_depth = max_expansion_depth
        self.provides_versioning = provides_versioning
        self.supported_collections_operations = [] if not supported_collections_operations else supported_collections_operations
        self.supported_model_types = [] if not supported_model_types else supported_model_types

signatures = {
    frozenset(
        'provides_collection_pids',
        'collection_pid_provider_type',
        'enforces_access, supports_pagination',
        'asynchronous_actions',
        'rule_based_generation',
        'max_expansion_depth',
        'provides_versioning',
        'supported_collections_operations',
        'supported_model_types'
    ): Service
}