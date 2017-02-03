
from enum import Enum
from flask.json import JSONEncoder, JSONDecoder
from .models import Model


class RDAJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Model):
            return obj.dict()
        if isinstance(obj, Enum):
            return obj.name

class RDAJSONDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        self.orig_obj_hook = kwargs.pop("object_hook", None)
        super(APIJSONDecoder, self).__init__(*args, object_hook=self.custom_obj_hook, **kwargs)

    def custom_obj_hook(self, dct):

        # Calling custom decode function:
        dct = HelperFunctions.jsonDecodeHandler(dct)
        if (self.orig_obj_hook):  # Do we have another hook to call?
            return self.orig_obj_hook(dct)  # Yes: then do it
        return dct  # No: just return the decoded dictreturn super(MyJSONEncoder, self).default(obj)
