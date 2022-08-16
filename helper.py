import configparser


# Method to read config file settings
def read_config():
    config = configparser.ConfigParser()
    config.read('/home/konstip/SUScraper/configuration.ini')
    return config
