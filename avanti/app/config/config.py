import logging.config
import yaml
import os

from .dict import Dict
from .logconf import get_config

_logger_ = logging.getLogger('default')

class ConfigError(Exception):
    pass


def parse_config(filename='config.yaml') -> Dict:
    s = _read_file(filename)
    config = _parse_config(s)
    log_conf = get_config(config)
    config.update(update_config(config))
    logging.config.dictConfig(log_conf)
    return Dict(config)


def _parse_config(s: str) -> dict:
    data = yaml.load(s, Loader=yaml.SafeLoader)
    return data


def _read_file(filename):
    if not filename:
        raise ConfigError(f'invalid config file: {filename}')
    with open(filename, encoding='utf-8') as f:
        return f.read()

def update_config(config):
    upd_conf = {}

    db_params = config.get('db', {})
    if not db_params:
        _logger_.info('DB parameters is missing in config file!')
        db_params['host'] = os.environ.get('DB_HOST', 'localhost')
        db_params['port'] = os.environ.get('DB_PORT', '3306')
    if any(var not in os.environ for var in ('DB_NAME', 'DB_USER', 'DB_PASS')):
        _logger_.error('DB parameters is missing in environment!')
    else:
        db_params['db_name'] = os.environ.get('DB_NAME')
        db_params['user'] = os.environ.get('DB_USER')
        db_params['pass'] = os.environ.get('DB_PASS')
    upd_conf['db_url'] = _get_db_url(db_params)

    return upd_conf


def _get_db_url(db_params: dict):
    try:
        user = db_params['user']
        password = db_params['pass']
        db_name = db_params['db_name']
        host = db_params['host']
        port = db_params['port']
    except KeyError as err:
        raise ConfigError(f'DB connect failed, missing parameter {err}')
    # mysql://avanti:dthbabrfwbz2@localhost:3306/avanti
    return f'mysql://{user}:{password}@{host}:{port}/{db_name}'
