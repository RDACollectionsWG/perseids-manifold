import random, string
from src.collections.models import *
from src.members.models import *
from src.service.models import *
from run import app


class RandomGenerator:

    def collection(self):
        with app.app_context():
            id = ''.join(random.choice(string.printable) for _ in range(random.randint(10, 30)))
            return CollectionObject.apply({
                "id": id,
                "capabilities": CollectionCapabilities.apply({
                    "isOrdered": random.choice([True, False]),
                    "appendsToEnd": random.choice([True, False]),
                    "supportsRoles": random.choice([True, False]),
                    "membershipIsMutable": random.choice([True, False]),
                    "metadataIsMutable": random.choice([True, False]),
                    "restrictedToType": "",
                    "maxLength": 5
                }),
                "properties": CollectionProperties.apply({
                    "ownership": "perseids:me",
                    "license": "CCbySA",
                    "modelType": "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md",
                    "hasAccessRestrictions": random.choice([True, False]),
                    "memberOf": [],
                    "descriptionOntology": "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md"
                }),
                "description": ''.join(random.choice(string.printable) for _ in range(random.randint(30, 50)))
            })

    def member(self):
        return MemberItem(''.join(random.choice(string.printable) for _ in range(random.randint(10, 30))),
                          ''.join(random.choice(string.printable) for _ in range(random.randint(10, 30))))

    def service(self):
        return Service.apply({
            "providesCollectionPids": random.choice([True, False]),
            "collectionPidProviderType": random.choice([True, False]),
            "enforcesAccess": random.choice([True, False]),
            "supportsPagination": random.choice([True, False]),
            "asynchronousActions": random.choice([True, False]),
            "ruleBasedGeneration": random.choice([True, False]),
            "maxExpansionDepth": random.choice([True, False]),
            "providesVersioning": random.choice([True, False]),
            "supportedCollectionsOperations": ["findMatch","flatten"],
            "supportedModelTypes": []
        })

    def json_collection(self):
        return """
        {
          "id": "urn:cite:test_collections.1",
          "capabilities": {
            "isOrdered": true,
            "appendsToEnd": false,
            "supportsRoles": false,
            "membershipIsMutable": true,
            "metadataIsMutable": true,
            "restrictedToType": "",
            "maxLength": 5
          },
          "properties": {
            "ownership": "perseids:me",
            "license": "CCbySA",
            "modelType": "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md",
            "hasAccessRestrictions": false,
            "memberOf": [],
            "descriptionOntology": "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md"
          },
          "description": ""
        }
        """
