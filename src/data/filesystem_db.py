from flask.json import load, dump
import os
import random
import string
from os import listdir, remove
from os.path import abspath, isdir, join
from shutil import rmtree
from .db import DBInterface


class FilesystemDB(DBInterface):

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

    def get_collection(self, cid=None):
        if cid is None:
            ids = [d for d in listdir(self.d_data) if isdir(join(self.d_data, d))]
            return self.get_collection(ids)
        else:
            if not type(cid) in (type([]), type(()), type(set())):
                cid = [cid]
            return [self.__load_json__(join(self.d_data, id.replace('/', '∕'), self.d_collection)) for id in cid]

    def get_member(self, cid, mid=None):
        assert cid
        if mid is None:
            return self.get_member(cid, [m[:-5] for m in listdir(join(self.d_data, cid.replace('/', '∕'))) if (m.endswith('.json') and m != self.d_collection)])
        else:
            if not type(mid) in (type([]), type(()), type(set())):
                mid = [mid]
            return [self.__load_json__(join(self.d_data, cid.replace('/', '∕'), id.replace('/', '∕')+'.json')) for id in mid]

    def get_service(self):
        return self.__load_json__(join(self.d_data, self.d_service))

    def set_service(self, sObject):
        self.__write_json__(join(self.d_data, self.d_service), sObject)

    '''
        @:returns CollectionObject or Error
    '''
    def set_collection(self,cObject):
        filename = join(self.d_data, cObject.id.replace('/', '∕'), self.d_collection)
        self.__write_json__(filename, cObject)
        return cObject

    def set_member(self, cid, mObject):
        filename = join(self.d_data, cid.replace('/', '∕'), mObject.id.replace('/', '∕')+'.json')
        self.__write_json__(filename, mObject)
        return mObject

    def del_collection(self, cid):
        filename = join(self.d_data, cid.replace('/', '∕'))
        rmtree(filename)
        return True

    def del_member(self, cid, mid):
        filename = join(self.d_data, cid.replace('/', '∕'), mid.replace('/', '∕')+'.json')
        remove(filename)
        return True

    def get_id(self, type_class):
        return ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 30)))

db = FilesystemDB()
