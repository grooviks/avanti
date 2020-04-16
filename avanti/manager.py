#!/usr/bin/env python

import gunicorn.app.base
import logging.config
import sys

from flask_script import Manager, Command, Option
from flask_migrate import Migrate, MigrateCommand

from avanti.app import application
from avanti.app.config import parse_config
from avanti.app.extensions import db

_logger_ = logging.getLogger('default')


class GunicornApp(gunicorn.app.base.BaseApplication):
    """Gunicorn application class for run flask app"""
    def __init__(self, flask_app, **kwargs):
        _logger_.debug('Initializing gunicorn')
        self.flask_app = flask_app
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', '8000')
        self.workers = kwargs.get('workers_count', '2')
        self.access_log = kwargs.get('access_log', 'access.log')
        self.error_log = kwargs.get('error_log', 'error.log')
        self.reload_type = True
        self.timeout = 30
        super(GunicornApp, self).__init__()

    def load_config(self):
        _logger_.debug('Loading gunicorn configs')
        self.cfg.set('workers', self.workers)
        self.cfg.set('reload', self.reload_type)
        self.cfg.set('timeout', self.timeout)
        self.cfg.set('accesslog', self.access_log)
        self.cfg.set('errorlog', self.error_log)
        self.cfg.set('access_log_format', '%(t)s "%(r)s" %(s)s %(b)s %(L)s')
        self.cfg.set('bind', f'{self.host}:{self.port}')
        self.cfg.set('worker_connections', 1)
        _logger_.info('gunicorn configs loaded')

    def load(self):
        return self.flask_app


class GunicornServer(Command):

    description = 'Run the app within Gunicorn'

    def __init__(self, filename='config.yaml'):
        self.filename = filename
        self.config = parse_config(filename=self.filename)

    def get_options(self):
        return (
            Option('-c', '--config',
                   dest='config',
                   default=self.filename),
        )

    def run(self, *args, **kwargs):
        config = self.config.get('gunicorn')

        _logger_.debug('Preparing gunicorn server')
        try:
            gunicorn_app = GunicornApp(
                flask_app=application(),
                **config
            )
        except Exception as err:
            _logger_.error('Server failed')
            _logger_.fatal(f'Error {err}, occurred when init gunicorn application exit', exc_info=True)
            return sys.exit(1)
        _logger_.debug('Running gunicorn app')
        try:
            gunicorn_app.run()
        except Exception as _e:
            _logger_.error('Gunicorn app failed')
            _logger_.exception(_e)
            raise


app = application()
# app.config.from_object(os.environ['APP_SETTINGS'])
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)
manager.add_command('gunicorn', GunicornServer)
manager.add_command('runserver', GunicornServer)

if __name__ == '__main__':
    manager.run()
