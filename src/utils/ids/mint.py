import abc, random, requests, string
from src.collections.models import CollectionObject
from src.members.models import MemberItem

class IDGenerator(object, metaclass=abc.ABCMeta):

    def __init__(self, template=None):
        self.template = template

    @abc.abstractmethod
    def get_id(self, cls):
        pass

class URNGenerator(IDGenerator):

    def __init__(self, template="urn:cite:{}.{}"):
        IDGenerator.__init__(self,template)

    def get_id(self, cls):
        if cls is CollectionObject:
            return self.template.format("collections",''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 30))))
        elif cls is MemberItem:
            return self.template.format("items",''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 30))))
        else:
            raise TypeError

class RemoteGenerator(IDGenerator):

    def __init__(self, template="http://annotation.perseids.org/id/{}"):
        IDGenerator.__init__(self,template)

    def get_id(self, cls):

        if cls is CollectionObject or cls is MemberItem:
            res = requests.get(self.template.format("collection" if cls is CollectionObject else "member"))
            if res.status_code is 200:
                return res.content
            else:
                raise ConnectionError
        else:
            raise TypeError

class NullGenerator(IDGenerator):

    def get_id(self, cls):
        return 'id:'+''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 30)))
