def resolve(obj):
    if isinstance(obj, Model):
        return obj.dict()
    else:
        return obj

class Model(object):

    @classmethod
    def apply(cls, dct):
        try:
            return cls(**dct)
        except:
            return None

    def dict(self):
        return {key: resolve(value) for key, value in self.__dict__.items() if not key.startswith("__") and value is not None}
