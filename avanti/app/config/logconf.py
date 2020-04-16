def get_config(config: dict):
    config = config.get('logger', {})
    default_config = config.get('default', {})
    access_config = config.get('access', {})
    formatter = 'default'
    handlers = ['default', 'console']
    level = 'DEBUG'

    return {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[{asctime}] [{module} -> {pathname}:{lineno}] ({process} -> {thread}]) [{levelname}] >> {message}',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': formatter,
            },
            'default': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': formatter,
                'filename': default_config.get('filename', 'avanti.log'),
                'maxBytes': default_config.get('size', 500000000),
                'backupCount': default_config.get('count', 6),
            },
            'access': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': access_config.get('filename', 'access.log'),
                'maxBytes': access_config.get('size', 500000000),
                'backupCount': access_config.get('count', 4),
            }
        },
        'loggers': {
            'default': {
                'handlers': default_config.get('handlers', handlers),
                'level': default_config.get('level', level),
                'propagate': False,
            },
            'access': {
                'handlers': access_config.get('handlers', handlers),
                'level': access_config.get('level', level),
                'propagate': False,
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['default', 'console'],
        },
    }
