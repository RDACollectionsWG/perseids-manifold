from src.data.filesystem_db import FilesystemDB
from src.data.ldp_db import LDPDataBase

class Config(object):
    RDA_API_DB = LDPDataBase
    RDA_API_LOCATION = "http://localhost:8080/marmotta"

class ComposeConfig(Config):
    RDA_API_LOCATION = "http://marmotta:8080/marmotta"

class FilesystemDBConfig(object):
    RDA_API_DB = FilesystemDB
    RDA_API_LOCATION = './data'