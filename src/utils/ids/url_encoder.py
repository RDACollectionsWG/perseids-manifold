import base64

from src.utils.base.struct import Struct

encoder = Struct(
    encode = lambda s: base64.b64encode(str.encode(s)).decode(),
    decode = lambda s: base64.b64decode(s).decode()
)