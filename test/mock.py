import random, string
from src.collections.models import *
from src.members.models import *


class RandomGenerator:

    def collection(self):
        with app.app_context():
            id = ''.join(random.choice(string.printable) for _ in range(random.randint(10, 30)))
            return CollectionObject.apply({
                "id": id,
                "capabilities": {
                    "isOrdered": random.choice([True, False]),
                    "appendsToEnd": random.choice([True, False]),
                    "supportsRoles": random.choice([True, False]),
                    "membershipIsMutable": random.choice([True, False]),
                    "metadataIsMutable": random.choice([True, False]),
                    "restrictedToType": "",
                    "maxLength": 5
                },
                "properties": {
                    "ownership": "perseids:me",
                    "license": "CCbySA",
                    "modelType": "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md",
                    "hasAccessRestrictions": random.choice([True, False]),
                    "memberOf": [],
                    "descriptionOntology": "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md"
                },
                "description": ""
            })

    def member(self):
        return MemberItem(''.join(random.choice(string.printable) for _ in range(random.randint(10, 30))),
                          ''.join(random.choice(string.printable) for _ in range(random.randint(10, 30))))
