import serial
import GPS
import pyipc
import os
import logging
import setproctitle
from compass_web import get_heading
import time

ser = serial.Serial('/dev/ttyAMA0')
gps = GPS.GPS(ser)


#####   Logging   #####
logging.basicConfig(filename='motion-control.log', format='[%(levelname)-7s] : %(asctime)s : %(name)-8s : %(message)s',
                    level=logging.DEBUG, datefmt='%b %d, %g | %H:%M:%S')
log = logging.getLogger(__name__)


#####   IPC   #####
setproctitle.setproctitle('process-motion_control')
shared_data = {'gps': {'latitude': 0.0, 'longitude': 0.0, 'satellite': 0}, 'compass': 0.0,
               'velocity': 0.0, 'destination': {'latitude': 0.0, 'longitude': 0.0}, 'toggleSignal': None}


def ipc_handler(signal, frame):
    global shared_data
    print('new-data obtained')
    shared_data = ipc.get_data()
    print(shared_data)

try:
    shared_file_path = os.environ['SHARED_FILE_PATH']
    lock_file_path = os.environ['LOCK_FILE_PATH']
    log.info('Path for shared file and lock file obtained')
    ipc = pyipc.IPC('process-motion_control', 'process-api',
                    shared_file_path, lock_file_path, ipc_handler)
    ipc.connect()
except KeyError:
    print('Error : Unable to obtain SHARED_FILE_PATH or LOCK_FILE_PATH in environment variables')
    log.error('Error obatining shared or lock file path')

# while True:
#     print(get_heading())
#     time.sleep(.1)
def get_location():
    latitude = gps.latitude[0] + gps.latitude[1] / 60.0
    longitude = gps.longitude[0] + gps.longitude[1] / 60.0
    return (latitude, longitude)
print('here')