import geopy
import time
import struct

serial_handler = None
live_location_handler = None
heading handler = None
def float32ToBytes(num):
    x = struct.pack('f', num)
    _bytes = list(int(ch) for ch in x)
    return _bytes
 
def angle_diff(inp, _set):
    tmp = abs(inp - _set)
    diff = min(tmp, abs(360.0 - tmp))
    if (_set + diff) != inp and (_set - diff) != inp:
        if (inp + diff) >= 360.0:
            return diff
        else:
            return -diff
    else:
        return (_set - inp)


def getTheta(coord_1, coord_2):
    delta = coord_2[1] - coord_1[1]
    desired_heading = math.atan2(math.sin(delta)*math.cos(coord_2[0]), math.cos(coord_1[0])*math.sin(coord_2[0])-math.sin(coord_1[0])*math.cos(coord_2[0])*math.cos(delta))
    if desired_heading < 0.0:
        desired_heading += 360.0
    retrun desired_heading

# Distance calculation in cms
def getDist(coord_1, coord_2):  
    return geopy.distance.geodesic(coord_1, coord_2).meters * 100

def send_signal(vel, curr_angle, desired_angle):
    _bytes = [int(vel)&0xFF]
    _bytes += float32ToBytes(curr_angle)
    _bytes += float32ToBytes(desired_angle)
    

def move(vel, desired_angle):
    send_signal(vel, heading_handler(), desired_angle)

def rotate(desired_angle):
    while abs(angle_diff(heading_handler(), desired_angle)):
        send_signal(0, heading_handler(), desired_angle)
        time.sleep(.05)

def moveTowardsCoordinate(coord_dest):
    rotate(getTheta(get_live_location(), coord_dest))
    while getDist(live_location_handler(), coord_dest) >50:
        move(30, getTheta(live_location_handler(), coord_dest))
        time.sleep(.05)