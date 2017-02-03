
from enum import Enum
from flask.json import JSONEncoder, JSONDecoder
from .models import Model
from ..service.models import signatures as s_service
from ..collections.models import signatures as s_collections
from ..members.models import signatures as s_members

signatures = s_service + s_collections + s_members

class RDAJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Model):
            return obj.dict()
        if isinstance(obj, Enum):
            return obj.name
        return super(RDAJSONEncoder, self).default(obj)

class RDAJSONDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        self.orig_obj_hook = kwargs.pop("object_hook", None)
        super(RDAJSONDecoder, self).__init__(*args, object_hook=self.custom_obj_hook, **kwargs)

    def custom_obj_hook(self, dct):
        res = dct
        try:
            res = signatures[frozenset(dct.keys())](dct)
        finally:
            # Calling custom decode function:
            if self.orig_obj_hook & res==dct:  # Do we have another hook to call?
                res = self.orig_obj_hook(dct)  # Yes: then do it
        return res  # No: just return the decoded dict
