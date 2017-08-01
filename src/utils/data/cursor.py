class cursor:

    def __init__(self, start=0, end=None):
        self.start = start if start else 0
        self.end = int(end) if end else None
        self.offset = int(end)-int(start) if end else None

    def next(self):
        if self.end:
            offset = self.end - self.start
            return cursor(self.end, self.end+offset)
        else:
            return cursor()

    def prev(self):
        if self.start and self.end:
            offset = self.end - self.start
            return cursor(self.start-offset, self.start)
        else:
            return cursor()

    def toString(self):
        start = str(self.start) if self.start else 0
        offset = str(self.end-int(start)) if self.end else ''
        return "{}_{}".format(start,offset) if start or offset else None

    @classmethod
    def fromString(cls, string):
        start,offset = string.split("_") if "_" in string else (0,None)
        start = int(start) if start else 0
        end = start+int(offset) if offset else None
        return cursor(start,end)
