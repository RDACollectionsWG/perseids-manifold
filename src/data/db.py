from flask.json import load, dump
import os
import random
import string
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
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename,"w") as file:
            dump(object, file)

    def getCollections(self, cid=None):
        if cid is None:
            ids = [d for d in listdir(self.d_data) if isdir(join(self.d_data, d))]
            return self.getCollections(ids)
        else:
            if not type(cid) in (type([]), type(()), type(set())):
                cid = [cid]
            return [self.__load_json__(join(self.d_data, id.replace('/', '∕'), self.d_collection)) for id in cid]

    def getMembers(self, cid, mid=None):
        assert cid
        if mid is None:
            return self.getMembers(cid, [m[:-5] for m in listdir(join(self.d_data, cid.replace('/', '∕'))) if (m.endswith('.json') and m != self.d_collection)])
        else:
            if not type(mid) in (type([]), type(()), type(set())):
                mid = [mid]
            return [self.__load_json__(join(self.d_data, cid.replace('/', '∕'), id.replace('/', '∕')+'.json')) for id in mid]

    def getService(self):
        return self.__load_json__(join(self.d_data, self.d_service))

    def setService(self, sObject):
        self.__write_json__(join(self.d_data, self.d_service), sObject)

    '''
        @:returns CollectionObject or Error
    '''
    def setCollection(self,cObject):
        filename = join(self.d_data, cObject.id.replace('/', '∕'), self.d_collection)
        self.__write_json__(filename, cObject)
        return cObject

    def setMember(self, cid, mObject):
        filename = join(self.d_data, cid.replace('/', '∕'), mObject.id.replace('/', '∕')+'.json')
        self.__write_json__(filename, mObject)
        return mObject

    def delCollection(self, cid):
        filename = join(self.d_data, cid.replace('/', '∕'))
        rmtree(filename)
        return True

    def delMember(self, cid, mObject):
        filename = join(self.d_data, cid.replace('/', '∕'), mObject.id.replace('/', '∕')+'.json')
        remove(filename)
        return True

    def mintID(self):
        return ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 30)))

db = DataBase()
