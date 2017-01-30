from ..collections.models import *
from ..members.models import *
from ..service.models import *

cites = {
    'urn:cite:test_collections.1': CollectionObject(
        "urn:cite:test_collections.1",
        CollectionCapabilities(True, False, False, True, True, "", 5),
        CollectionProperties("perseids:me", "CCbySA", "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md", False, [], "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md"),
        ""
    ),
    'urn:cite:test_collections.2': CollectionObject(
        "urn:cite:test_collections.2",
        CollectionCapabilities(True, False, False, True, True, "", 5),
        CollectionProperties("perseids:me", "CCbySA", "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md", False, [], "https://github.com/perseids-project/CITE-JSON-LD/blob/master/templates/img/SCHEMA.md"),
        ""
    )
}

members = {
    "http://example.org/mem/1": MemberItem("http://example.org/mem/1","http://example.org/loc/1"),
    "http://example.org/mem/2": MemberItem("http://example.org/mem/2","http://example.org/loc/2"),
    "http://example.org/mem/3": MemberItem("http://example.org/mem/3","http://example.org/loc/3"),
    "http://example.org/mem/4": MemberItem("http://example.org/mem/4","http://example.org/loc/4"),
    "http://example.org/mem/5": MemberItem("http://example.org/mem/5","http://example.org/loc/5")
}

service = Service(supported_collections_operations=[Operations.findMatch, Operations.flatten])
