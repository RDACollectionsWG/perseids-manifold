from ..collections.models import *
from ..members.models import *
from ..service.models import *
from flask.json import load, dump
from os import listdir, remove
from os.path import abspath, isdir, join
from shutil import rmtree

class DataBase:

    def __init__(self, d_data='data', d_collection='_collection.json', d_service='_service.json'):
        self.d_data = d_data
        self.d_collection = d_collection
        self.d_service = d_service

    def __load_json__(self, filename):
        with open(filename) as filecontent:
            return load(filecontent)

    def __write_json__(self, filename, object):
        with open(filename) as file:
            dump(object, file)

    def getCollections(self, cid=None):
        if not cid:
            return self.getCollections([d for d in listdir(self.d_data) if isdir(join(self.d_data, d))])
        else:
            if not type(cid) in (type([]), type(()), type(set())):
                cid = [cid]
            return [CollectionObject(**self.__load_json__(join(self.d_data, id.replace('/', '∕'), self.d_collection))) for id in cid]

    def getMembers(self, cid, mid=None):
        assert cid
        if not mid:
            return self.getMembers(cid, [m[:-5] for m in listdir(join(self.d_data, cid.replace('/', '∕'))) if (m.endswith('.json') and m != self.d_collection)])
        else:
            if not type(mid) in (type([]), type(()), type(set())):
                mid = [mid]
            return [MemberItem(**self.__load_json__(join(self.d_data, cid.replace('/', '∕'), id.replace('/', '∕')+'.json'))) for id in mid]

    def getService(self):
        return Service(self.__load_json__(join(self.d_data, self.d_service)))
    '''
        @:returns CollectionObject or Error
    '''
    def setCollection(self,cObject):
        try:
            filename = join(self.d_data, cObject.id.replace('/', '∕'), self.d_collection)
            self.__write_json__(filename, cObject)
            return cObject
        except:
            raise Exception()

    def setMember(self, cid, mObject):
        try:
            filename = join(self.d_data, cid.replace('/', '∕'), mObject.id.replace('/', '∕')+'.json')
            self.__write_json__(filename, mObject)
            return mObject
        except:
            raise Exception()

    def delCollection(self, cid):
        try:
            filename = join(self.d_data, cid.replace('/', '∕'))
            rmtree(filename)
            return True
        except:
            raise Exception()

    def delMember(self, cid, mObject):
        try:
            filename = join(self.d_data, cid.replace('/', '∕'), mObject.id.replace('/', '∕'))
            remove(filename)
            return True
        except:
            raise Exception()

db = DataBase()
