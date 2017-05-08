from flask import Flask
from src.data.ldp_db import LDPDataBase

class CollectionsAPI(Flask):

    def __init__(self, name):
        super(CollectionsAPI, self).__init__(name)
        self.db = LDPDataBase("http://localhost:8080/marmotta")
