import random, string, json

from rdflib import URIRef, Literal, Graph
from rdflib.namespace import RDF, DCTERMS
from rdflib.plugins.sparql.results.jsonresults import JSONResult

from run import app
from src.collections.models import *
from src.members.models import *
from src.service.models import *
from src.utils.conversions.rda import RDA
from src.utils.ids.url_encoder import encoder
from src.utils.rdf.ldp import LDP as ldp

LDP = ldp.ns

class RandomGenerator:

    def collection(self):
        with app.app_context():
            id = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 30)))
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
                "description": {'something': u''.join(random.choice(string.printable) for _ in range(random.randint(30, 50)))+"\u00f6"}#"\u00f6"}
            })

    def member(self):
        return MemberItem(''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 30))),
                          ''.join(random.choice(string.printable) for _ in range(random.randint(10, 30))))

    def service(self):
        return Service.apply({
            "providesCollectionPids": random.choice([True, False]),
            "collectionPidProviderType": ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 30))),
            "enforcesAccess": random.choice([True, False]),
            "supportsPagination": random.choice([True, False]),
            "asynchronousActions": random.choice([True, False]),
            "ruleBasedGeneration": random.choice([True, False]),
            "maxExpansionDepth": random.randint(-1, 10),
            "providesVersioning": random.choice([True, False]),
            "supportedCollectionOperations": ["findMatch","flatten"],
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
          "description": {
            "something": "new"
          }
        }
        """

    def json_member(self):
        return """
        {
          "id": "http://example.org/mem/1",
          "location": "http://example.org/loc/1"
        }
        """

    def json_service(self):
        return """
        {
          "providesCollectionPids": true,
          "collectionPidProviderType": true,
          "enforcesAccess": true,
          "supportsPagination": true,
          "asynchronousActions": true,
          "ruleBasedGeneration": true,
          "maxExpansionDepth": -1,
          "providesVersioning": true,
          "supportedCollectionOperations": ["findMatch","flatten"],
          "supportedModelTypes": []
        }
        """

    def graph_collection(self, ldp_root, obj=None):
        if not obj:
            obj = self.collection()
        node = URIRef(ldp_root+encoder.encode(obj.id))
        capabilities = URIRef(node+"#capabilities")
        properties = URIRef(node+"#properties")
        description = URIRef(node+"#description")

        g = Graph(identifier=node)
        g.add((node, RDF.type, RDA.Collection))
        g.add((node, DCTERMS.identifier, Literal(obj.id)))
        g.add((node, RDA.hasCapabilities, capabilities))
        g.add((node, RDA.hasProperties, properties))
        g.add((node, DCTERMS.description, description))
        g.add((capabilities, RDA.isOrdered, Literal(obj.capabilities.isOrdered)))
        g.add((capabilities, RDA.appendsToEnd, Literal(obj.capabilities.appendsToEnd)))
        g.add((capabilities, RDA.maxLength, Literal(obj.capabilities.maxLength)))
        g.add((capabilities, RDA.membershipIsMutable, Literal(obj.capabilities.membershipIsMutable)))
        g.add((capabilities, RDA.metadataIsMutable, Literal(obj.capabilities.metadataIsMutable)))
        g.add((capabilities, RDA.restrictedToType, Literal(obj.capabilities.restrictedToType)))
        g.add((capabilities, RDA.supportsRoles, Literal(obj.capabilities.supportsRoles)))
        g.add((properties, RDA.memberOf, RDF.nil))
        g.add((properties, RDA.modelType, Literal(obj.properties.modelType)))
        g.add((properties, RDA.descriptionOntology, Literal(obj.properties.descriptionOntology)))
        g.add((properties, DCTERMS.license, Literal(obj.properties.license)))
        g.add((properties, DCTERMS.rightsHolder, Literal(obj.properties.ownership)))
        g.add((properties, RDA.hasAccessRestrictions, Literal(obj.properties.hasAccessRestrictions)))
        g.add((description, URIRef(description+"@something"), Literal(obj.description['something'])))
        return g

    def graph_member(self, ldp_root, c_id, obj=None):
        if not obj:
            obj = self.member()
        node = URIRef(ldp_root+encoder.encode(c_id)+"/member/"+encoder.encode(obj.id))
        mappings = URIRef(node+"#mappings")

        g = Graph(identifier=node)
        g.add((node, RDF.type, RDA.Member))
        g.add((node, DCTERMS.identifier, Literal(obj.id)))
        g.add((node, RDA.location, Literal(obj.location)))
        if hasattr(obj, 'datatype'):
            g.add((node, RDA.datatype, Literal(obj.datatype)))
        if hasattr(obj, 'ontology'):
            g.add((node, RDA.ontology, Literal(obj.ontology)))
        if hasattr(obj, 'mappings'):
            g.add((node, RDA.mappings, mappings))
            if hasattr(obj, 'mappings.role'):
                g.add((mappings, RDA.role, Literal(obj.mappings.role)))
            if hasattr(obj, 'mappings.index'):
                g.add((mappings, RDA.index, Literal(obj.mappings.index)))
            if hasattr(obj, 'mappings.dateAdded'):
                g.add((mappings, RDA.dateAdded, Literal(obj.mappings.dateAdded)))
        return g
        
    def graph_service(self, ldp_root, obj=None):
        if not obj:
            obj = self.service()
        node = URIRef(ldp_root+"service")
        
        g = Graph(identifier=node)
        g.add((node, RDF.type, RDA.Service))
        g.add((node, RDA.providesCollectionPids, Literal(obj.providesCollectionPids)))
        g.add((node, RDA.collectionPidProviderType, Literal(obj.collectionPidProviderType)))
        g.add((node, RDA.enforcesAccess, Literal(obj.enforcesAccess)))
        g.add((node, RDA.supportsPagination, Literal(obj.supportsPagination)))
        g.add((node, RDA.asynchronousActions, Literal(obj.asynchronousActions)))
        g.add((node, RDA.ruleBasedGeneration, Literal(obj.ruleBasedGeneration)))
        g.add((node, RDA.maxExpansionDepth, Literal(obj.maxExpansionDepth)))
        g.add((node, RDA.providesVersioning, Literal(obj.providesVersioning)))
        for sco in obj.supportedCollectionOperations:
            g.add((node, RDA.supportedCollectionOperations, Literal(sco)))
        if len(obj.supportedCollectionOperations) is 0:
            g.add((node, RDA.supportedCollectionOperations, RDF.nil))
        for smt in obj.supportedModelTypes:
            g.add((node, RDA.supportedModelTypes, Literal(smt)))
        if len(obj.supportedModelTypes) is 0:
            g.add((node, RDA.supportedModelTypes, RDF.nil))
        return g

    #def result(self):
     #   graph = self.graph_service("")
      #  g = graph.identifier

    def collection_result(self,obj=None, ldp_root="http://localhost:8080/marmotta/ldp/"):
        if not obj:
            obj = self.collection()
            ldp = ldp_root+encoder.encode(obj.id)
        return JSONResult(json.loads("""
{{
  "head" : {{
    "vars" : [ "g", "s", "p", "o" ]
  }},
  "results" : {{
    "bindings" : [ {{
      "o" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#Resource"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
      }}
    }}, {{
      "o" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#RDFSource"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
      }}
    }}, {{
      "o" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#Container"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#interactionModel"
      }}
    }}, {{
      "o" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#Container"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
      }}
    }}, {{
      "o" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#BasicContainer"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
      }}
    }}, {{
      "o" : {{
        "datatype" : "http://www.w3.org/2001/XMLSchema#dateTime",
        "type" : "literal",
        "value" : "2017-05-25T11:18:11.000Z"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://purl.org/dc/terms/created"
      }}
    }}, {{
      "o" : {{
        "datatype" : "http://www.w3.org/2001/XMLSchema#dateTime",
        "type" : "literal",
        "value" : "2017-05-25T11:18:11.000Z"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://purl.org/dc/terms/modified"
      }}
    }}, {{
      "o" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp_root}"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/ns/ldp#contains"
      }}
    }}, {{
      "o" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#Collection"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
      }}
    }}, {{
      "o" : {{
        "type" : "uri",
        "value" : "{ldp}#capabilities"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#hasCapabilities"
      }}
    }}, {{
      "o" : {{
        "type" : "uri",
        "value" : "{ldp}#properties"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#hasProperties"
      }}
    }}, {{
      "o" : {{
        "type" : "uri",
        "value" : "{obj.id}"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://purl.org/dc/terms/identifier"
      }}
    }}, {{
      "o" : {{
        "type" : "uri",
        "value" : "{ldp}#description"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://purl.org/dc/terms/description"
      }}
    }}, {{
      "o" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#Capabilities"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#capabilities"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
      }}
    }}, {{
      "o" : {{
        "datatype" : "http://www.w3.org/2001/XMLSchema#boolean",
        "type" : "literal",
        "value" : "false"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#capabilities"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#isOrdered"
      }}
    }}, {{
      "o" : {{
        "datatype" : "http://www.w3.org/2001/XMLSchema#boolean",
        "type" : "literal",
        "value" : "false"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#capabilities"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#appendsToEnd"
      }}
    }}, {{
      "o" : {{
        "datatype" : "http://www.w3.org/2001/XMLSchema#boolean",
        "type" : "literal",
        "value" : "false"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#capabilities"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#supportsRoles"
      }}
    }}, {{
      "o" : {{
        "datatype" : "http://www.w3.org/2001/XMLSchema#boolean",
        "type" : "literal",
        "value" : "false"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#capabilities"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#membershipIsMutable"
      }}
    }}, {{
      "o" : {{
        "datatype" : "http://www.w3.org/2001/XMLSchema#boolean",
        "type" : "literal",
        "value" : "false"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#capabilities"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#metadataIsMutable"
      }}
    }}, {{
      "o" : {{
        "type" : "literal",
        "value" : ""
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#capabilities"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#restrictedToType"
      }}
    }}, {{
      "o" : {{
        "datatype" : "http://www.w3.org/2001/XMLSchema#integer",
        "type" : "literal",
        "value" : "-1"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#capabilities"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#maxLength"
      }}
    }}, {{
      "o" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#Properties"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#properties"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
      }}
    }}, {{
      "o" : {{
        "type" : "literal",
        "value" : ""
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#properties"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#ownership"
      }}
    }}, {{
      "o" : {{
        "type" : "literal",
        "value" : ""
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#properties"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://purl.org/dc/terms/license"
      }}
    }}, {{
      "o" : {{
        "type" : "literal",
        "value" : ""
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#properties"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#modelType"
      }}
    }}, {{
      "o" : {{
        "datatype" : "http://www.w3.org/2001/XMLSchema#boolean",
        "type" : "literal",
        "value" : "false"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#properties"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#hasAccessRestrictions"
      }}
    }}, {{
      "o" : {{
        "type" : "uri",
        "value" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#properties"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#memberOf"
      }}
    }}, {{
      "o" : {{
        "type" : "literal",
        "value" : "{obj.properties.descriptionOntology}"
      }},
      "g" : {{
        "type" : "uri",
        "value" : "{ldp}"
      }},
      "s" : {{
        "type" : "uri",
        "value" : "{ldp}#properties"
      }},
      "p" : {{
        "type" : "uri",
        "value" : "http://rd-alliance.org/ns/collections#descriptionOntology"
      }}
    }} ]
  }}
}}
        """.format(obj=obj, ldp=ldp, ldp_root=ldp_root)))
