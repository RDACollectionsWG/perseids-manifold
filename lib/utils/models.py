class Model(object):

    @classmethod
    def apply(cls, dct):
        try:
            return cls(**dct)
        except:
            return None

    def dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith("__")}
