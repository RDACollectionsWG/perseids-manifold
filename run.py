from flask import Flask

from src.collections.routes import routes as r_collections
from src.members.routes import routes as r_members
from src.service.routes import routes as r_service
from src.utils.errors import activate
from src.utils.json import *

app = Flask(__name__)
app.json_encoder = RDAJSONEncoder
app.json_decoder = RDAJSONDecoder
activate(app)

for (url, kwargs) in r_service + r_collections + r_members:
    app.add_url_rule(url, **kwargs)
