from src.utils.data.ldp_db import *
from test.mock import RandomGenerator

mocks = RandomGenerator()
c_obj = mocks.collection()
ldp = LDPDataBase("http://localhost:32768/marmotta")
