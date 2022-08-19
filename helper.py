import configparser
import pathlib
import os

# Method to read config file settings
def read_config():
    config = configparser.ConfigParser()
    config.read(os.path.join(pathlib.Path(__file__).parent.absolute(), 'configuration.ini'))
    return config
