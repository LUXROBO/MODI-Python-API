# -*- coding: utf-8 -*-

"""Serial Task module."""

from __future__ import absolute_import

import serial
import serial.tools.list_ports as stl
import time
import queue


class SerialTask(object):
    def __init__(self, serial_read_q, serial_write_q, port):
        super(SerialTask, self).__init__()
        self._serial_read_q = serial_read_q
        self._serial_write_q = serial_write_q
        self._port = port

    def list_ports(self):
        """
        :return: an iterable that yields :py:class:`~serial.tools.list_ports.ListPortInfo` objects.

        The function returns an iterable that yields tuples of three strings:

        * port name as it can be passed to :py:class:`modi.modi.MODI`
        * description in human readable form
        * sort of hardware ID. E.g. may contain VID:PID of USB-serial adapters.

        Items are returned in no particular order. It may make sense to sort the items. Also note that the reported strings are different across platforms and operating systems, even for the same device.
        
        .. note:: Support is limited to a number of operating systems. On some systems description and hardware ID will not be available (``None``).

        :platform: Posix (/dev files)
        :platform: Linux (/dev files, sysfs)
        :platform: OSX (iokit)
        :platform: Windows (setupapi, registry)
        """
        ports = stl.comports()
        modi_ports = list()

        for port in ports:
            if (
                port.manufacturer == "LUXROBO"
                or port.product == "MODI Network Module"
                or port.description == "MODI Network Module"
                or (port.vid == 12254 and port.pid == 2)
            ):
                modi_ports.append(port)

        return modi_ports

    def connect_serial(self):
        # Sereial Connection Once
        if self._port is None:
            ports = self.list_ports()
            if len(ports) > 0:
                self._serial = serial.Serial(ports[0].device, 921600)
            else:
                raise serial.SerialException("No MODI network module connected.")
        else:
            self._serial = serial.Serial(self._port, 921600)

    def disconnect_serial(self):
        self._serial.close()

    def start_thread(self):

        # print('SerialTask : ', os.getpid())
        # Main Thread 2ms loop
        # while True:
        # read serial
        self.read_serial()
        # write serial
        self.write_serial()
        time.sleep(0.005)
        # self._serial.close()

    ##################################################################

    def read_serial(self):
        if self._serial.in_waiting != 0:
            read_temp = self._serial.read(self._serial.in_waiting).decode()
            self._serial_read_q.put(read_temp)

    def write_serial(self):

        try:
            writetemp = self._serial_write_q.get_nowait().encode()
        except queue.Empty:
            pass
        else:
            self._serial.write(writetemp)
            # print(writetemp)
            time.sleep(0.001)

        # # # Write Display Data
        # try:
        #     writedisplaytemp = self._display_send_q.get_nowait().encode()
        # except queue.Empty:
        #     pass
        # else:
        #     self._serial.write(writedisplaytemp)
        #     time.sleep(0.001)
