from flask.json import load, dump
import os
import random
import string
from os import listdir, remove
from os.path import abspath, isdir, join
from shutil import rmtree
from .db import DBInterface
from src.utils.base.errors import NotFoundError, DBError


class FilesystemDB(DBInterface):

    def __init__(self, d_data='data', d_collection='_collection.json', d_service='_service.json'):
        self.d_data = d_data
        self.d_collection = d_collection
        self.d_service = d_service

    def __load_json__(self, filename):
        try:
            with open(filename) as filecontent:
                return load(filecontent)
        except FileNotFoundError:
            raise NotFoundError()
        except:
            raise DBError()

    def __write_json__(self, filename, object):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename,"w") as file:
                dump(object, file)
        except FileNotFoundError:
            raise NotFoundError()
        except:
            raise DBError()

    def ask_collection(self, c_id):
        pass

    def ask_member(self, c_id, m_id):
        pass

    def get_collection(self, c_id=None):
        if c_id is None:
            ids = [d for d in listdir(self.d_data) if isdir(join(self.d_data, d))]
            return self.get_collection(ids)
        else:
            if not type(c_id) in (type([]), type(()), type(set())):
                c_id = [c_id]
            result = [self.__load_json__(join(self.d_data, id.replace('/', '∕'), self.d_collection)) for id in c_id]
            return [c for c in result if c is not None]

    '''
        @:returns CollectionObject or Error
    '''
    def set_collection(self, c_obj):
        filename = join(self.d_data, c_obj.id.replace('/', '∕'), self.d_collection)
        self.__write_json__(filename, c_obj)
        return c_obj


    def del_collection(self, c_id):
        try:
            filename = join(self.d_data, c_id.replace('/', '∕'))
            rmtree(filename)
            return True
        except FileNotFoundError:
            raise NotFoundError()
        except:
            raise DBError()

    def upd_collection(self, c_obj):
        self.del_collection(c_obj.id)
        self.set_collection(c_obj)
        return c_obj

    def get_member(self, c_id, m_id=None):
        if m_id is None:
            return self.get_member(c_id, [m[:-5] for m in listdir(join(self.d_data, c_id.replace('/', '∕'))) if (m.endswith('.json') and m != self.d_collection)])
        else:
            if not type(m_id) in (type([]), type(()), type(set())):
                m_id = [m_id]
            return [self.__load_json__(join(self.d_data, c_id.replace('/', '∕'), id.replace('/', '∕')+'.json')) for id in m_id]

    def set_member(self, c_id, m_obj):
        filename = join(self.d_data, c_id.replace('/', '∕'), m_obj.id.replace('/', '∕')+'.json')
        self.__write_json__(filename, m_obj)
        return m_obj

    def del_member(self, c_id, m_id):
        try:
            filename = join(self.d_data, c_id.replace('/', '∕'), m_id.replace('/', '∕')+'.json')
            remove(filename)
            return True
        except FileNotFoundError:
            raise NotFoundError()
        except:
            raise DBError()

    def upd_member(self, c_id, m_obj):
        self.del_member(c_id, m_obj.id)
        self.set_member(c_id, m_obj)
        return m_obj

    def get_service(self):
        return self.__load_json__(join(self.d_data, self.d_service))

    def set_service(self, s_obj):
        self.__write_json__(join(self.d_data, self.d_service), s_obj)


    def get_id(self, type_class):
        return ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 30)))

db = FilesystemDB()
