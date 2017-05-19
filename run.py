import os

from flask import send_from_directory
from flask_cors import CORS

from config import Config, FilesystemDBConfig, ComposeConfig
from src.app import CollectionsAPI
from src.collections.routes import routes as r_collections
from src.members.routes import routes as r_members
from src.service.routes import routes as r_service
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
    return send_from_directory("www","swagger.json")
app.add_url_rule("/apidocs", methods=["GET"], view_func=apidocs)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
