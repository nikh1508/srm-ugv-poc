import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import logging
import pyipc
from flask_cors import CORS
import setproctitle

#####   Logging   #####
logging.basicConfig(filename='server.log', format='[%(levelname)-7s] : %(asctime)s : %(name)-8s : %(message)s',
                    level=logging.DEBUG, datefmt='%b %d, %g | %H:%M:%S')
log = logging.getLogger(__name__)


#####   IPC   #####
setproctitle.setproctitle('process-api')
shared_data = {'gps': {'latitude': 0.0, 'longitude': 0.0, 'satellite': 0}, 'compass': 0.0,
               'velocity': 0.0, 'destination': {'latitude': 0.0, 'longitude': 0.0}, 'toggleSignal': None}


def ipc_handler(signal, frame):
    print('new-data')
    global shared_data
    shared_data = ipc.get_data()


try:
    shared_file_path = os.environ['SHARED_FILE_PATH']
    lock_file_path = os.environ['LOCK_FILE_PATH']
    log.info('Path for shared file and lock file obtained')
    ipc = pyipc.IPC('process-api', 'process-motion_control',
                    shared_file_path, lock_file_path, ipc_handler)
    ipc.connect()
except KeyError:
    print('Error : Unable to obtain SHARED_FILE_PATH or LOCK_FILE_PATH in environment variables')
    log.error('Error obatining shared or lock file path')


#####   Flask App   #####
app = Flask(__name__)
CORS(app)
app.config.from_pyfile('config.py')

#####   Database   #####
db = SQLAlchemy(app)
ma = Marshmallow(app)

from routes import *

if __name__ == "__main__":
    log.info('Starting Flask Sever.')
    # app.run()
    app.run(host='0.0.0.0', port=80)