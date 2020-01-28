from micropyGPS import MicropyGPS
import serial
import threading
import pyipc

gps_serial = serial.Serial('/dev/ttyAMA0')
gps = MicropyGPS()

class GPS(threading.Thread):
    latitude = gps.latitude
    longitude = gps.longitude
    fix_stat = gps.fix_stat
    fix_type = gps.fix_type
    satellites_in_use = gps.satellites_in_use
    satellites_visibles = gps.satellites_visible
    speed = gps.speed
    time_since_fix = gps.time_since_fix()

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            ch = gps_serial.read()
            try:                    
                ch = ch.decode()
                ret = gps.update(ch)
                if ret != None:
                    self.update_values()
            except:
                # Do nothing if Serial exception occurs
                pass
    
    def update_values(self):
        self.latitude = gps.latitude
        self.longitude = gps.longitude
        self.fix_stat = gps.fix_stat
        self.fix_type = gps.fix_type
        self.satellites_in_use = gps.satellites_in_use
        self.satellites_visibles = gps.satellites_visible
        self.speed = gps.speed
        self.time_since_fix = gps.time_since_fix()