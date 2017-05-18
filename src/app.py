from flask import Flask

from src.utils.data.null_db import NullDB


class CollectionsAPI(Flask):

    def __init__(self, name):
        super(CollectionsAPI, self).__init__(name)
        self.db = NullDB()

    def initialize(self, db):
        self.db = db
        #self.service = db.get_service()