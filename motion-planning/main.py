import serial
import GPS
import pyipc
import os
import logging
import setproctitle
from compass_web import get_heading
import time
import threading
from motion import *

ser = serial.Serial('/dev/ttyAMA0', timeout=0)
gps = GPS.GPS(ser)

bot_power = False

def power_stat():
    global bot_power
    return bot_power
#####   Logging   #####
logging.basicConfig(filename='motion-control.log', format='[%(levelname)-7s] : %(asctime)s : %(name)-8s : %(message)s',
                    level=logging.DEBUG, datefmt='%b %d, %g | %H:%M:%S')
log = logging.getLogger(__name__)


#####   IPC   #####
setproctitle.setproctitle('process-motion_control')
shared_data = {'gps': {'latitude': None, 'longitude': None, 'satellite': None}, 'compass': {'heading': None},
               'velocity': 0.0, 'destination': {'latitude': None, 'longitude': None}, 'toggleSignal': None}


def ipc_handler(signal, frame):
    global shared_data, bot_power
    print('new-data obtained')
    shared_data = ipc.get_data()
    # signal = 'startSignal' if shared_data['startSignal'] else ('stopSignal' if shared_data['stopSignal'] else None)
    # if signal is not None:
    #     bot_power = signal == 'startSignal'
    #     with ipc.lock:
    #         shared_data[signal] = False
    #         ipc.send_data(shared_data)
    if shared_data['toggleSignal'] is not None:
        bot_power = shared_data['toggleSignal'] == 'start'
        shared_data['toggleSignal'] = None
        with ipc.lock:
            shared_data['toggleSignal'] = False
            ipc.send_data(shared_data)
        
    # print(shared_data)

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

# serial_handler = ser
# live_location_handler = get_location
# heading_handler = get_heading

def comm_arduino():
    global param
    while True:
        param['heading_now'] = get_heading()
        send_signal(param['vel'], param['heading_now'], param['heading_desired'], ser)
        time.sleep(.1)

def sensor_update_subroutine():
    global shared_data
    while True:
        location_now = get_location()
        heading = get_heading
        with ipc.lock:
            shared_data['gps']['latitude'] = location_now[0]
            shared_data['gps']['longitude'] = location_now[1]
            shared_data['compass']['heading'] = get_heading() 
            ipc.send_data(shared_data)
        time.sleep(.7)

prevStopped = True

subroutine1 = threading.Thread(target=comm_arduino)
subroutine2 = threading.Thread(target=sensor_update_subroutine)

def Main():
    global bot_power
    # moveTowardsCoordinate((1,2), get_location, get_heading, power_stat)
    subroutine1.start()
    subroutine2.start()
    while True:
        if bot_power:
            print('on')
            prevStopped = False 
            if(shared_data['destination']['latitude'] is not None):
                coord_dest = (shared_data['destination']['latitude'], shared_data['destination']['longitude'])
                moveTowardsCoordinate(coord_dest, get_location, get_heading, power_stat)
            bot_power = False
        else:
            print('stopped')
            prevStopped = True
            move(3, 0.0)
        time.sleep(.5)


if __name__ == '__main__':
    Main()