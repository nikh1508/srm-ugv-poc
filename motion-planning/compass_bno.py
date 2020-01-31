import threading
import serial
import time

bno = serial.Serial('/dev/ttyUSB0', 115200, timeout=.5)
compass_heading = -1.0

def readBNO():
    global compass_heading
    try:
        bno.write(b'g')
        response = bno.readline().decode()
        if response != '':
            compass_heading = float(response.split('\r')[0])
    except:
        pass

def readContinuous():
    while True:
        readBNO()
        time.sleep(.1)

bno_thread = threading.Thread(target=readContinuous)
bno_thread.start()

def get_heading():
    return compass_heading

if __name__ == '__main__':
    while True:
        print(get_heading())
        time.sleep(.1)