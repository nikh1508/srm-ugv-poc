import geopy.distance
import time
import struct
import math
# serial_handler = None
# live_location_handler = None
# heading_handler = None
param = {'vel':3, 'heading_now': -1.0, 'heading_desired': -1.0}

#### Serial Part ####
startMarker = 254
endMarker = 255
specialByte = 253

def encodeToString(data):
    global startMarker, specialByte, specialByte
    outString = ""
    outString = outString + chr(startMarker)
    for val in data:
        if val >= specialByte:
            outString = outString + chr(specialByte)
            outString = outString + chr(val - specialByte)
        else:
            outString = outString + chr(val)
    outString = outString + chr(endMarker)
    return outString

def writeSerial(toSend, serial_handler):
    serial_handler.write(encodeToString(toSend).encode('latin_1'))

##########################

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
    return desired_heading

# Distance calculation in cms
def getDist(coord_1, coord_2):  
    return geopy.distance.geodesic(coord_1, coord_2).meters * 100

def send_signal(vel, curr_angle, desired_angle, serial_handler):
    _bytes = [int(vel)&0xFF]
    _bytes += float32ToBytes(curr_angle)
    _bytes += float32ToBytes(desired_angle)
    writeSerial(_bytes, serial_handler)
    

def move(vel, desired_angle):
    global param
    param['vel'] = vel
    param['desired_angle'] = desired_angle

def rotate(desired_angle, heading_handler, power_stat):
    while abs(angle_diff(heading_handler(), desired_angle)) > 5.0 and power_stat():
        # send_signal(0, heading_handler(), desired_angle, )
        move(0, desired_angle)
        time.sleep(.05)

def moveTowardsCoordinate(coord_dest, live_location_handler, heading_handler, power_stat):
    print('moving towards', coord_dest, heading_handler)
    rotate(getTheta(live_location_handler(), coord_dest), heading_handler, power_stat)
    while getDist(live_location_handler(), coord_dest) >50 and power_stat():
        move(30, getTheta(live_location_handler(), coord_dest))
        time.sleep(.05)