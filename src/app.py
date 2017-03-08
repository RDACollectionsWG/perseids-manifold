from flask import Flask
from src.data.db import DataBase

class CollectionsAPI(Flask):

    def __init__(self, name):
        super(CollectionsAPI, self).__init__(name)
        self.db = DataBase()