from configparser import ConfigParser

from .core import Core
from src.utils import Logger, Validation

def load_configuration() -> ConfigParser:
    configuration = ConfigParser()
    configuration.read('./config.ini')
    return configuration

if __name__ == "__main__":
    config = load_configuration()

    arguments = Validation.parse_arguments(config)
    Logger.log('Unknown', 'info', f'IP: {arguments.ip}')
    Logger.log('Unknown', 'info', f'Port: {arguments.port}')
    Logger.log('Unknown', 'info', f'Init Node: {arguments.initial}')

    if Validation.open_port(arguments.ip, arguments.port):
        Logger.log('Unknown', 'error', f'Port is occupied: {arguments.port}')
        exit(1)

    api = Core(arguments.ip, int(arguments.port), arguments.initial)

    if True: api.cli()
    else: pass # WebAPP

    exit(0)
    