2017-08-30

Pull Request #69 (https://github.com/RDACollectionsWG/perseids-manifold/pull/69)
introduced changes in the data model to correspond with changes in the 
v1.0.0 of the RDA Collections API Specification. These changes require updates
to existing data structures stored with prior version of Perseids Manifold code.
SPARQL Update statements to effect these changes are provided below:


```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rda: <http://rd-alliance.org/ns/collections#>
INSERT {
  GRAPH ?g {?s ?p owl:Nothing}
} WHERE {
  GRAPH ?g {?s ?p rda:Empty}
};

DELETE WHERE {
  ?s ?p <http://rd-alliance.org/ns/collections#Empty>.
};

PREFIX rda: <http://rd-alliance.org/ns/collections#>
PREFIX dcterms: <http://purl.org/dc/terms/>
INSERT {
 GRAPH ?g {?s rda:dateCreated ?o}
} WHERE {
  GRAPH ?g { ?t rda:hasProperties ?s }
  ?t dcterms:created ?o .
};

PREFIX rda: <http://rd-alliance.org/ns/collections#>
INSERT {
 GRAPH ?g {?s rda:propertiesAreMutable ?o}
} WHERE {
 GRAPH ?g {?s rda:metadataIsMutable ?o}
};

DELETE WHERE {
 ?s rda:metadataIsMutable ?o.
};

```
