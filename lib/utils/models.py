class Model(object):
    def dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith("__")}
