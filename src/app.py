from flask import Flask
from src.data.filesystem_db import FilesystemDB

class CollectionsAPI(Flask):

    def __init__(self, name):
        super(CollectionsAPI, self).__init__(name)
        self.db = FilesystemDB()
