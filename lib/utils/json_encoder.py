from enum import Enum
from flask.json import JSONEncoder
from .models import Model


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Model):
            return obj.dict()
        if isinstance(obj, Enum):
            return obj.name
        return super(MyJSONEncoder, self).default(obj)
