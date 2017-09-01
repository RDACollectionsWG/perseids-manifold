## Perseids Manifold

[![Build Status](https://travis-ci.org/RDACollectionsWG/tufts-implementation.svg?branch=master)](https://travis-ci.org/RDACollectionsWG/tufts-implementation)
[![Coverage Status](https://coveralls.io/repos/github/RDACollectionsWG/tufts-implementation/badge.svg?branch=master)](https://coveralls.io/github/RDACollectionsWG/tufts-implementation?branch=master)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.801786.svg)](https://doi.org/10.5281/zenodo.801786)

### RDA Collections API
- - - - - - - - - -

Manifold is a research collections server developed at the Perseids Project of the Department of Classic at Tufts University, Boston. It serves as a demonstrator for the work of the Research Data Alliance’s Collections Working Group API. The server provides a general purpose CRUD interface to interact with research data collections in realtime and manage data points in recursive and/or overlapping collections.

The Research Data Collections Working Group has been running from 03/2016 until 09/2017, and has been an effort aimed at collaboratively designing a web interface for sharing data, as well as tools and specifications surrounding research collections across academic disciplines and institutions. Its main documentation can be found in the working group’s [Github organization](https://github.com/RDACollectionsWG) (including a [Swagger API documentation](https://rdacollectionswg.github.io/apidocs)) and a case statement as well as the archived mailing list is available [on the RDA website](https://www.rd-alliance.org/groups/research-data-collections-wg.html).

### Getting started
- - - - - - - - -

Currently there are two documented ways to get a Manifold collections server up and running.

#### Docker Compose (recommended)
The project provides a `docker-compose.yml` file and a simple environment can started up by running `docker-compose up` in the project folder. To enable database persistence, add a `volumes` definition to the `marmotta` image in the composition file.

#### Local installation

To run the application locally, we clone the repo to a local folder.
**1.** `git clone https://github.com/rdacollectionswg/perseids-manifold && cd perseids-manifold`.

Then create a virtual environment to encapsulate the application and its dependencies:.
**2.** `virtualenv -p /usr/local/bin/python3 manifold-env && source manifold-env/bin/activate`

Inside the virtual environment, install the dependencies.
**3.** `python setup.py install`

To configure the database and application entry point, use environmental variables. See section on Configuration for details.
**4.** `export COLLECTIONS_API_ENV=default && export FLASK_APP=run.py`

Finally, start up the Flask server.
**5.** `flask run`

**Dependencies**

In the recommended configuration (default), Manifold requires a triple store with SPARQL endpoint to save collections data. The application has been developed and tested with Apache Marmotta, but other systems will work as well. Using the (optional) LDP interface with databases other than Marmotta may require changes to the LDP and SPARQL components.

Apache Marmotta is available as a Docker image (install [`apache/marmotta`](https://hub.docker.com/r/apache/marmotta/) from Docker Hub) or can be run locally using the Tomcat application server.

### Configuration
- - - - - - - - - - -

Manifold uses a simple configuration object to set up the database and ID generation subsystems. A set of predefined configurations is provided in config.py, and the selected configuration can be updated with environmental variables. Alternatively, configurations can be provided as environmental variables, JSON files, Python files or programmatically as Python objects, see `flask.config` for details.
 
### Architecture
- - - - - - -

Perseids Manifold has been implemented in Python using the Flask HTTP Framework. It is designed in a layered architecture spanning from the HTTP interface to the database drivers and thereby provides separation of concerns and intermediate-level programming interfaces across all layers.

Following the layout of the [specification](https://rdacollectionswg.github.io/apidocs), _models_ and _controllers_ have been grouped into Collections, Members and Service. The _data models_ primarily provide a set of classes that are identical mappings of the working group specification to Python, and functions to translate between those and JSON representations which are being used for server-client communications.

The _controllers_ read out request parameters, perform the conversions, check the request’s validity against Service and Collection properties, and call the DB interface.

### Data model
- - - - - - - - - -

The data model implements the definitions found in the working group specification, and extends them with base class that provides a pair of functions to facilitate type conversions and unified processing throughout the DB layer.

The DB Interface is formulated at the level of Python objects according to the application models and serves as a shared model across different DB drivers. The DB drivers implement a lot of the functionality, since this enables developers to optimize queries individually to each database model.

`RDAJSONEncoder` and `RDAJSONDecoder` provide implicit JSON encoding and decoding to support automatic data conversions of request and response bodies.

### DB Interface
- - - - - - - - -

The DB Interface is shared across implementations and is meant to unify queries across different database types, thus enabling addition of new database drivers and reuse of drivers for customized frontends.

The interface has been formulated in terms of the application models for collections and items, filters and cursors. A translation into database specific queries happens inside the individual implementations. It is up to the implementation to either interpret and apply the filters and cursor to query results or to translate them directly into the respective database query language and run them natively on the database.

### LDP DB
- - - - - - - - - - -

`ldp_db` implements the Manifold DB interface as an access layer to an RDF database with a SPARQL endpoint. To this end it maps the RDA Collection model into a set of RDF named graphs according to a supplied ontology (as `entry` to the `dictionary`, see below), provides conversion mechanisms, and support classes and templates for communication with SPARQL endpoints.

### RDF Libraries
- - - - - - - - - -
#### Mapping tool
Invoke the class constructor with an `rdflib.Namespace` and a `src.utils.rdf.dictionary`. The Namespace is not being used in the class, but exposed for convenient use in the scope surrounding an instantiated mapping tool.
The mapping tool provides 2 high-level methods — `object_to_graph` and `graph_to_object` — to convert between object- and graph-representations and vice-versa. Both functions work agnostic to the type of object(s) that is/are being converted and identify the relevant dictionary entries by way of looking at the argument type. Internally, the methods rely on another set of functions — `dict_to_graph` and `graph_to_dict` — and a dictionary data structure which is described in more detail below.
The `object_to_graph` method is 1-to-1 and returns a single graph in response to a single object (and a node URI), whereas the `graph_to_object` method will parse an array of (zero, one, or more) objects from a single graph.
The mapping tool can perform arbitrary transformations according to whichever object-graph-mapping definitions are being loaded into its dictionary.
#### Dictionary
Dictionaries provide a unified point of access to multiple `entries` with ontology metadata (object-graph-mappings). Individual entries can be retrieved using an object’s or RDF resource’s data type as key in the dictionary.
#### Entry
Entries are used to manage ontology metadata for single classes of data from the RDA Collections specification. Their constructor takes a class object, its respective RDA-namespaced identifier and specifically formatted (Python) dictionary with information to translate between attributes and RDF triples. When added to a dictionary it is addressable both through the object type and the type’s URI (in string form).

### SPARQL
- - - - - - - - - -

#### SPARQL Service
The SPARQLTools class provides a Python interface to SPARQL calls with rdflib-typed arguments. The constructor takes the sparql attributes of a Marmotta object to enable direct requests to the SPARQL endpoint. The methods take in `rdflib` URIRef IDs and Dataset graphs and populate the respective SPARQL templates from them. `SPARQLTools.list` accepts `Bind` and `Filter` arrays as a mechanism to implement filters at the query level.
#### SPARQLSet
`SPARQLSet` extends `JSONResult` with a method to return the result as a Dataset object. It further provides the `status_code` field as means to access the request’s HTTP code.

### Access Control
- - - - - - -

Manifold utilizes objects that implement `ACLInterface` to manage access control. The interface can get the current user’s ID, and set and get permissions objects for combinations of User, Collection and Member IDs. `Permissions` objects declare read (`r`), write (`w`) and delete (`x`) permissions.
