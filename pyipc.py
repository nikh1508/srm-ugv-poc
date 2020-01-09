##
#   Inter-Process Communication using a shared file and external signals
#   Author: Nikhil Kumar,
#           SRM Team Robocon,
#           SRMIST, Chennai, IN
##
import signal as _signal
from subprocess import check_output as _check_output
import time as _time
import threading as _threading
import logging as _logging
from filelock import FileLock as _FileLock
import json as _json


class IPC(_threading.Thread):
    __is_connected = False
    __other_process_pid = None

    def __init__(self, self__process_name, other_process_name, shared_file_path, lock, signal_handler, debug=False):
        _threading.Thread.__init__(self)
        self.__self_name = self__process_name
        self.__other_process_name = other_process_name
        self.__debug = debug
        self.__log = _logging.getLogger(__name__)
        self.__shared_file_path = shared_file_path
        _signal.signal(_signal.SIGUSR1, signal_handler)
        # Use this lock while mutating shared data-structure or it may happen 
        # that before you call send_data the data the other process resets the date to be sent.
        self.lock = _FileLock(lock)

    def get_pid(self, process_name):
        all_process = _check_output(['ps', 'aux']).decode().split('\n')
        pid = []
        for process in all_process:
            if process_name in process:
                pid.append(process.split()[1])
        if len(pid) == 0:
            return - 1
        elif len(pid) > 1:
            return - 2
        else:
            return int(pid[0])

    def connect(self):
        self.start()

    def __debug_msg(self, debug_msg, lev='info'):
        if self.__debug:
            print(debug_msg)
        if lev == 'info':
            self.__log.info(debug_msg)
        elif lev == 'error':
            self.__log.error(debug_msg)

    def run(self):
        while True:
            self.__other_process_pid = self.get_pid(self.__other_process_name)
            self.__debug_msg('Trying to obtain PID of {}'.format(
                self.__other_process_name))
            while self.__other_process_pid < 0:
                self.__other_process_pid = self.get_pid(
                    self.__other_process_name)
                _time.sleep(.1)
            self.__debug_msg('Obtained PID of {}'.format(
                self.__other_process_name))
            self.__is_connected = True
            while self.__is_connected:
                _time.sleep(2)
            self.__debug_msg('Reconnecting to {}'.format(
                self.__other_process_name))

    def is_connected(self):
        return self.__is_connected

    def __trigger_signal(self):
        try:
            output = _check_output(
                ['kill', '-30', str(self.__other_process_pid)]).decode()
        except Exception as e:
            self.__is_connected = False
            self.__debug_msg('Disconnected from {}. Error: {}'.format(
                self.__other_process_name, str(e)), 'error')

    def send_data(self, data):
        if self.__is_connected:
            with self.__lock:
                open(self.__shared_file_path, 'w').write(_json.dumps(data, indent=3, sort_keys=True))
            self.__trigger_signal()
        else:
            self.__debug_msg(
                'Cannot send new data since the process is disconnected', 'error')

    def get_data(self):
        with self.__lock:
            data = _json.loads(open(self.__shared_file_path, 'r').read())
        return data
