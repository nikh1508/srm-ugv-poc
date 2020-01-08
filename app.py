import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import logging

#####   Logging   #####
logging.basicConfig(filename='server.log', format='[%(levelname)-7s] : %(asctime)s : %(name)-8s : %(message)s',
                    level=logging.DEBUG, datefmt='%b %d, %g | %H:%M:%S')
log = logging.getLogger(__name__)


#####   IPC   #####
try:
    shared_file_path = os.environ['SHARED_FILE_PATH']
except KeyError:
    log.error('Error obatining shared file path')


#####   Flask App   #####
app = Flask(__name__)
app.config.from_pyfile('config.py')

#####   Database   #####
db = SQLAlchemy(app)
ma = Marshmallow(app)

from routes import *

if __name__ == "__main__":
    log.info('Starting Flask Sever.')
    app.run()
