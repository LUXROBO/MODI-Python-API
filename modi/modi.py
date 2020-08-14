"""Main MODI module."""

import atexit
import time
from importlib import import_module as im
from typing import Optional, Tuple

from modi._exe_thrd import ExeThrd
from modi.util.conn_util import is_network_module_connected, is_on_pi, \
    AIModuleFaultsException, AIModuleNotFoundException
from modi.util.misc import module_list
from modi.util.stranger import check_complete
from modi.util.topology_manager import TopologyManager
from modi.firmware_updater import STM32FirmwareUpdater, ESP32FirmwareUpdater
from modi.module.ai_module.ai_camera import AICamera
from modi.module.ai_module.ai_speaker import AISpeaker
from modi.module.ai_module.ai_mic import AIMic


class MODI:

    def __init__(self, conn_mode: str = "", verbose: bool = False,
                 port: str = None, uuid="", ai_mode: bool = True):
        self._modules = list()
        self._ai_modules = list()
        self._topology_data = dict()

        self._conn = self.__init_task(conn_mode, verbose, port, uuid)

        self._exe_thrd = ExeThrd(
            self._modules, self._topology_data, self._conn
        )
        print('Start initializing connected MODI modules')
        self._exe_thrd.start()

        self._topology_manager = TopologyManager(self._topology_data,
                                                 self._modules)

        init_time = time.time()

        if ai_mode:
            if not is_on_pi():
                raise AIModuleNotFoundException
            self._init_ai_modules()
            if len(self._ai_modules) > 1:
                print("MODI AI modules are initialized!")

        while not self._topology_manager.is_topology_complete():
            time.sleep(0.1)
            if time.time() - init_time > 5:
                print("MODI init timeout over. "
                      "Check your module connection.")
                break
        check_complete(self)
        print("MODI modules are initialized!")
        atexit.register(self.close)

    def _init_ai_modules(self) -> None:
        """Initialize AI Module features

        :return: None
        """
        try:
            self._init_ai_mic()
            self._init_ai_speaker()
            self._init_ai_camera()
        except AIModuleFaultsException as e:
            print(e)

    def _init_ai_camera(self) -> None:
        """Initialize AI Module's camera

        :return: None
        """
        self._ai_modules.append(AICamera())
        pass

    def _init_ai_mic(self) -> None:
        """Initialize AI Module's mic

        :return: None
        """
        self._ai_modules.append(AIMic())

    def _init_ai_speaker(self) -> None:
        """Initialize AI Module's speaker

        :return: None
        """
        self._ai_modules.append(AISpeaker())

    @staticmethod
    def __init_task(conn_mode, verbose, port, uuid):
        if not conn_mode:
            is_can = not is_network_module_connected() and is_on_pi()
            conn_mode = 'can' if is_can else 'ser'

        if conn_mode == 'ser':
            return im('modi.task.ser_task').SerTask(verbose, port)
        elif conn_mode == 'can':
            return im('modi.task.can_task').CanTask(verbose)
        elif conn_mode == 'ble':
            return im('modi.task.ble_task').BleTask(verbose, uuid)
        else:
            raise ValueError(f'Invalid conn mode {conn_mode}')

    def close(self):
        atexit.unregister(self.close)
        print("Closing MODI connection...")
        self._exe_thrd.close()
        self._conn.close_conn()

    def open(self):
        atexit.register(self.close)
        self._exe_thrd = ExeThrd(
            self._modules, self._topology_data, self._conn
        )
        self._conn.open_conn()
        self._exe_thrd.start()

    def send(self, message) -> None:
        """Low level method to send json pkt directly to modules

        :param message: Json packet to send
        :return: None
        """
        self._conn.send(message)

    def recv(self) -> Optional[str]:
        """Low level method to receive json pkt directly from modules

        :return: Json msg received
        :rtype: str if msg exists, else None
        """
        return self._conn.recv()

    def print_topology_map(self, print_id: bool = False) -> None:
        """Prints out the topology map

        :param print_id: if True, the result includes module id
        :return: None
        """
        self._topology_manager.print_topology_map(print_id)

    @property
    def modules(self) -> module_list:
        """Module List of connected modules except network module.
        """
        return module_list(self._modules)

    @property
    def networks(self) -> module_list:
        return module_list(self._modules, 'Network')

    @property
    def buttons(self) -> module_list:
        """Module List of connected Button modules.
        """
        return module_list(self._modules, 'button')

    @property
    def dials(self) -> module_list:
        """Module List of connected Dial modules.
        """
        return module_list(self._modules, "dial")

    @property
    def displays(self) -> module_list:
        """Module List of connected Display modules.
        """
        return module_list(self._modules, "display")

    @property
    def envs(self) -> module_list:
        """Module List of connected Env modules.
        """
        return module_list(self._modules, "env")

    @property
    def gyros(self) -> module_list:
        """Module List of connected Gyro modules.
        """
        return module_list(self._modules, "gyro")

    @property
    def irs(self) -> module_list:
        """Module List of connected Ir modules.
        """
        return module_list(self._modules, "ir")

    @property
    def leds(self) -> module_list:
        """Module List of connected Led modules.
        """
        return module_list(self._modules, "led")

    @property
    def mics(self) -> module_list:
        """Module List of connected Mic modules.
        """
        return module_list(self._modules, "mic")

    @property
    def motors(self) -> module_list:
        """Module List of connected Motor modules.
        """
        return module_list(self._modules, "motor")

    @property
    def speakers(self) -> module_list:
        """Module List of connected Speaker modules.
        """
        return module_list(self._modules, "speaker")

    @property
    def ultrasonics(self) -> module_list:
        """Module List of connected Ultrasonic modules.
        """
        return module_list(self._modules, "ultrasonic")

    @property
    def ai_mics(self) -> Tuple[AIMic]:
        """Tuple of connected :class:'~modi.module.ai_mic.AIMic' modules
        """

        return tuple([ai_module for ai_module in self._ai_modules
                      if isinstance(ai_module, AIMic)])

    @property
    def ai_speakers(self) -> Tuple[AISpeaker]:
        """Tuple of connected :class:'~modi.module.ai_speaker.AISpeaker'
        modules
        """

        return tuple([ai_module for ai_module in self._ai_modules
                      if isinstance(ai_module, AISpeaker)])

    @property
    def ai_cameras(self) -> Tuple[AICamera]:
        """Tuple of connected :class:'~modi.module.ai_camera.AICamera'
        modules
        """
        return tuple(
            [ai_module for ai_module in self._ai_modules
             if isinstance(ai_module, AICamera)])


def update_module_firmware():
    updater = STM32FirmwareUpdater()
    updater.update_module_firmware()


def update_network_firmware(stub=True, force=False):
    updater = ESP32FirmwareUpdater()
    updater.start_update(stub=stub, force=force)
