from .control import ACLInterface
from .permissions import Permissions

class NullACL(ACLInterface):

    def get_permission(self, uID=None, cID=None, mID=None):
        return Permissions(True, True, True)

    def set_permission(self, p, uID=None, cID=None, mID=None):
        return False

    def get_user(self):
        return 0