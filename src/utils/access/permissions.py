class Permissions(dict):

    def __init__(self, r=False, w=False, x=False):
        self.r = r
        self.w = w
        self.x = x