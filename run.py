from flask import Flask

from lib.service.routes import routes as r_service
from lib.collections.routes import routes as r_collections
from lib.members.routes import routes as r_members
from lib.utils.json_encoder import MyJSONEncoder
from lib.collections.errors import activate

app = Flask(__name__)
app.json_encoder = MyJSONEncoder
activate(app)

for (url, kwargs) in r_service + r_collections + r_members:
    app.add_url_rule(url, **kwargs)
