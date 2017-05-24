class Permissions(dict):

    def __init__(self, r=False, w=False, x=False):
        if not (isinstance(r,bool) and isinstance(w,bool) and isinstance(x,bool)):
            raise TypeError
        self.r = r
        self.w = w
        self.x = x