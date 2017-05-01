reset_marmotta = """
DELETE {?s ?p ?o}
INSERT {
  GRAPH <http://www.w3.org/ns/ldp#> {
    <http://localhost:32768/marmotta/ldp> <http://www.w3.org/2000/01/rdf-schema#label> "Marmotta's LDP Root Container" .
    <http://localhost:32768/marmotta/ldp> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/ldp#Resource> .
    <http://localhost:32768/marmotta/ldp> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/ldp#RDFSource> .
    <http://localhost:32768/marmotta/ldp> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/ldp#Container> .
    <http://localhost:32768/marmotta/ldp> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/ldp#BasicContainer> .
    <http://localhost:32768/marmotta/ldp> <http://www.w3.org/ns/ldp#interactionModel> <http://www.w3.org/ns/ldp#Container> .
    <http://localhost:32768/marmotta/ldp> <http://purl.org/dc/terms/created> "2017-03-15T13:41:19.000Z" .
    <http://localhost:32768/marmotta/ldp> <http://purl.org/dc/terms/modified> "2017-04-19T16:35:31.000Z"
  }
  GRAPH <http://localhost:32768/marmotta/context/cache> {
    <http://www.w3.org/ns/ldp#> <http://purl.org/dc/terms/created> "2015-02-26" .
    <http://www.w3.org/ns/ldp#> <http://purl.org/dc/terms/description> "Vocabulary URIs defined in the Linked Data Platform (LDP) namespace." .
    <http://www.w3.org/ns/ldp#> <http://purl.org/dc/terms/publisher> <http://www.w3.org/data#W3C> .
    <http://www.w3.org/ns/ldp#> <http://purl.org/dc/terms/title> "The W3C Linked Data Platform (LDP) Vocabulary" .
    <http://www.w3.org/ns/ldp#> <http://purl.org/vocab/vann/preferredNamespacePrefix> "ldp" .
    <http://www.w3.org/ns/ldp#> <http://purl.org/vocab/vann/preferredNamespaceUri> <http://www.w3.org/ns/ldp#> .
    <http://www.w3.org/ns/ldp#> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Ontology> .
    <http://www.w3.org/ns/ldp#> <http://www.w3.org/2000/01/rdf-schema#comment> "This ontology provides an informal representation of the concepts and terms as defined in the LDP specification.  Consult the LDP specification for normative reference." .
    <http://www.w3.org/ns/ldp#> <http://www.w3.org/2000/01/rdf-schema#label> "W3C Linked Data Platform (LDP)" .
    <http://www.w3.org/ns/ldp#> <http://www.w3.org/2000/01/rdf-schema#seeAlso> <http://www.w3.org/2011/09/LinkedData/> .
    <http://www.w3.org/ns/ldp#> <http://www.w3.org/2000/01/rdf-schema#seeAlso> <http://www.w3.org/2012/ldp> .
    <http://www.w3.org/ns/ldp#> <http://www.w3.org/2000/01/rdf-schema#seeAlso> <http://www.w3.org/TR/ldp-paging/> .
    <http://www.w3.org/ns/ldp#> <http://www.w3.org/2000/01/rdf-schema#seeAlso> <http://www.w3.org/TR/ldp-ucr/> .
    <http://www.w3.org/ns/ldp#> <http://www.w3.org/2000/01/rdf-schema#seeAlso> <http://www.w3.org/TR/ldp/> .
  }
} WHERE {?s ?p ?o}
"""

