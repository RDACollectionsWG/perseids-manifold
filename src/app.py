from flask import Flask

from src.utils.data.null_db import NullDB
from src.utils.access.null_control import NullACL
from src.utils.ids.mint import NullGenerator


class CollectionsAPI(Flask):

    def __init__(self, name):
        super(CollectionsAPI, self).__init__(name)
        self.db = NullDB()
        self.acl = NullACL()
        self.mint = NullGenerator()

    def initialize(self, config):
        if config.get('RDA_API_DB') and config.get('RDA_API_LOCATION'):
            self.db = config.get('RDA_API_DB')(config.get('RDA_API_LOCATION'))
        if config.get('RDA_API_ACL'):
            self.acl = config.get('RDA_API_ACL')
        if config.get('RDA_API_ID_GENERATOR'):
            self.mint = config.get('RDA_API_ID_GENERATOR')
        self.service = self.db.get_service()