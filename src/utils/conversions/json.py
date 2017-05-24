from enum import Enum

from flask.json import JSONEncoder, JSONDecoder

from src.collections.models import classList as m_collections
from src.members.models import classList as m_members
from src.service.models import classList as m_service
from src.utils.base.models import Model

models = m_service + m_collections + m_members

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
            objects = [n for n in [m.apply(dct) for m in models] if n]
            if (len(objects)==1):
                res=objects[0]
        finally:
            # Calling custom decode function:
            if self.orig_obj_hook and res==dct:  # Do we have another hook to call?
                res = self.orig_obj_hook(dct)  # Yes: then do it
        return res  # No: just return the decoded dict
