from src.data.db import DataBase
from src.collections.models import *
from unittest import TestCase, main
from tempfile import TemporaryDirectory, mkdtemp
import os
from run import app


class DbTests(TestCase):

    def setUp(self):
        self.dir = mkdtemp(dir='./test/data')
        self.db = DataBase(self.dir)
        self.app = app

    def test_db_create_collection(self):
        with app.app_context():
            cCap = CollectionCapabilities(**{
                "isOrdered": True,
                "appendsToEnd": False,
                "supportsRoles": False,
                "membershipIsMutable": True,
                "metadataIsMutable": True,
                "restrictedToType": "",
                "maxLength": 5
            })
            cProp = CollectionProperties(**{
                "ownership": "perseids:me",
                "license": "CCbySA",
                "modelType": "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md",
                "hasAccessRestrictions": False,
                "memberOf": [],
                "descriptionOntology": "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md"
            })
            cObj = CollectionObject(**{
                "id": "urn:cite:test_collections.1",
                "capabilities": cCap,
                "properties": cProp,
                "description": ""
            })
            self.db.setCollection(cObj)
            assert(os.path.isfile(os.path.join(self.db.d_data, cObj.id, self.db.d_collection)))

if __name__ == '__main__':
    main()
