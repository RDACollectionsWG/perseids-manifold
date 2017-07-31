import os

from flask import send_from_directory, request, jsonify, make_response
from flask_cors import CORS
from urllib.parse import urlparse

from config import Config, FilesystemDBConfig, ComposeConfig
from src.app import CollectionsAPI
from src.collections.routes import routes as r_collections
from src.members.routes import routes as r_members
from src.service.routes import routes as r_service
from src.utils.base.swagger import swagger
from src.utils.base.errors import activate
from src.utils.conversions.json import *

app = CollectionsAPI(__name__)

app.config.from_object({
    'filesystem': FilesystemDBConfig,
    'docker-compose': ComposeConfig,
    'default': Config
}.get(os.environ.get('COLLECTIONS_API_ENV'), Config))
if os.environ.get('COLLECTIONS_API_SETTINGS'):
    app.config.from_envvar('COLLECTIONS_API_SETTINGS')

app.initialize(app.config)

CORS(app)
app.json_encoder = RDAJSONEncoder
app.json_decoder = RDAJSONDecoder
activate(app)


for (url, kwargs) in r_service + r_collections + r_members:
    app.add_url_rule(url, **kwargs)

def index():
    return send_from_directory("www","index.html")
app.add_url_rule("/", methods=["GET"], view_func=index)

def apidocs():
    url = urlparse(request.url)
    if ":" in url.netloc:
        host, port = url.netloc.split(":")
    else:
        host = url.netloc
        port = "80"
    base_path = url.path.replace('/apidocs','') if url.path != "/apidocs" else "/"
    schemes = [url.scheme]
    other_scheme = "https" if url.scheme is "http" else "http"
    try:
        if request.get(other_scheme+"://"+url.netloc+url.path.replace('/apidocs','')+"/scheme").status_code is 200:
            schemes += [other_scheme]
    except:
        pass
    r = make_response(swagger.json(schemes, host, port, base_path))
    r.mimetype = 'application/json'
    return r
    # return send_from_directory("www","swagger.json")
app.add_url_rule("/apidocs", methods=["GET"], view_func=apidocs)

def scheme():
    return jsonify(""), 200
app.add_url_rule("/scheme", methods=["GET"], view_func=scheme)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
