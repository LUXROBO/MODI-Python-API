"""Main MODI module."""

import time
from typing import Dict, List, Tuple

import threading as th
import multiprocessing as mp
import os
import traceback
from pprint import pprint

from modi.topology_manager import TopologyManager

from modi._conn_proc import ConnProc
from modi._exe_thrd import ExeThrd

from modi.module.input_module.button import Button
from modi.module.input_module.dial import Dial
from modi.module.input_module.env import Env
from modi.module.input_module.gyro import Gyro
from modi.module.input_module.ir import Ir
from modi.module.input_module.mic import Mic
from modi.module.input_module.ultrasonic import Ultrasonic

from modi.module.output_module.display import Display
from modi.module.output_module.led import Led
from modi.module.output_module.motor import Motor
from modi.module.output_module.speaker import Speaker


class MODI:
    """
    Example:
    >>> import modi
    >>> bundle = modi.MODI()
    """

    def __init__(self, nb_modules: int, conn_mode: str = "serial",
                 module_uuid: str = "", test: bool = False):
        self._modules = list()
        self._module_ids = dict()
        self._topology_data = dict()

        self._recv_q = mp.Queue()
        self._send_q = mp.Queue()

        self._com_proc = None
        self._exe_thrd = None

        # Init flag used to notify initialization of MODI modules
        module_init_flag = th.Event()

        # If in test run, do not create process and thread
        if test:
            return

        self._com_proc = ConnProc(
            self._recv_q, self._send_q, conn_mode, module_uuid,
        )
        self._com_proc.daemon = True
        try:
            self._com_proc.start()
        except Exception:
            if os.name == 'nt':
                print('\nProcess initialization failed!\nMake sure you are '
                      'using\n    if __name__ == \'__main__\' \n '
                      'in the main module.')
            else:
                traceback.print_exc()
            exit(1)

        child_watch = \
            th.Thread(target=self.watch_child_process)
        child_watch.daemon = True
        child_watch.start()

        time.sleep(1)
        self._exe_thrd = ExeThrd(
            self._modules,
            self._module_ids,
            self._topology_data,
            self._recv_q,
            self._send_q,
            module_init_flag,
            nb_modules,
        )
        self._exe_thrd.daemon = True
        self._exe_thrd.start()
        time.sleep(1)

        self._topology_manager = TopologyManager(self._topology_data)
        module_init_timeout = 10 if conn_mode.startswith("ser") else 25
        module_init_flag.wait(timeout=module_init_timeout)
        if not module_init_flag.is_set():
            raise Exception("Modules are not initialized properly!")
            exit(1)
        print("MODI modules are initialized!")
        self.check_pong()

    def watch_child_process(self):
        while True:
            if not self._com_proc.is_alive():
                os._exit(1)
            time.sleep(0.05)

    def print_topology_map(self, print_id: bool = False):
        """Prints out the topology map

        :param print_id: if True, the result includes module id
        :return: None
        """
        self._topology_manager.print_topology_map(print_id)

    @property
    def modules(self):
        """Tuple of connected modules except network module.
        Example:
        >>> bundle = modi.MODI()
        >>> modules = bundle.modules
        """

        return tuple(self._modules)

    @property
    def buttons(self):
        """Tuple of connected :class:`~modi.module.button.Button` modules.
        """

        return tuple([module for module in self.modules
                      if isinstance(module, Button)])

    @property
    def dials(self):
        """Tuple of connected :class:`~modi.module.dial.Dial` modules.
        """

        return tuple([module for module in self.modules
                      if isinstance(module, Dial)])

    @property
    def displays(self):
        """Tuple of connected :class:`~modi.module.display.Display` modules.
        """

        return tuple([module for module in self.modules
                      if isinstance(module, Display)])

    @property
    def envs(self):
        """Tuple of connected :class:`~modi.module.env.Env` modules.
        """

        return tuple([module for module in self.modules
                      if isinstance(module, Env)])

    @property
    def gyros(self):
        """Tuple of connected :class:`~modi.module.gyro.Gyro` modules.
        """

        return tuple([module for module in self.modules
                      if isinstance(module, Gyro)])

    @property
    def irs(self):
        """Tuple of connected :class:`~modi.module.ir.Ir` modules.
        """

        return tuple([module for module in self.modules
                      if isinstance(module, Ir)])

    @property
    def leds(self):
        """Tuple of connected :class:`~modi.module.led.Led` modules.
        """

        return tuple([module for module in self.modules
                      if isinstance(module, Led)])

    @property
    def mics(self):
        """Tuple of connected :class:`~modi.module.mic.Mic` modules.
        """

        return tuple([module for module in self.modules
                      if isinstance(module, Mic)])

    @property
    def motors(self):
        """Tuple of connected :class:`~modi.module.motor.Motor` modules.
        """

        return tuple([module for module in self.modules
                      if isinstance(module, Motor)])

    @property
    def speakers(self):
        """Tuple of connected :class:`~modi.module.speaker.Speaker` modules.
        """

        return tuple([module for module in self.modules
                      if isinstance(module, Speaker)])

    @property
    def ultrasonics(self):
        """Tuple of connected :class:`~modi.module.ultrasonic.Ultrasonic` modules.
        """

        return tuple([module for module in self.modules
                      if isinstance(module, Ultrasonic)])

    def check_pong(self):
        module_names = [type(module).__name__ for module in self.modules]
        expected_names = ["Button", "Dial", "Led", "Speaker", "Display"]
        is_equal = len(module_names) == len(expected_names)
        if not is_equal:
            return
        else:
            for name in expected_names:
                if name not in module_names:
                    return

        cmd = input("You have found an easter egg!\nContinue??(y/n)")
        if cmd.lower() != 'y':
            return

        display = self.displays[0]
        button = self.buttons[0]
        led = self.leds[0]
        dial = self.dials[0]
        speaker = self.speakers[0]
        display.set_text("Press\nButton")
        while True:
            while True:
                if button.get_pressed():
                    display.set_text("PONG!!")
                    break
                time.sleep(0.02)
            time.sleep(1)
            point = self.game(display, led, speaker, dial)
            time.sleep(3)
            display.set_text("Game Over\nScore: " + str(point))
            time.sleep(2)
            display.set_text("Press Button to restart")

    @staticmethod
    def update_screen(pos, vel, bar, display):
        display.set_variable(0, pos[0], pos[1])
        display.set_variable(1, bar, 60)
        pos = (pos[0] + vel[0], pos[1] + vel[1])
        if pos[0] < 0 or pos[0] > 40:
            vel = (-vel[0], vel[1])
        if pos[1] < 0 or pos[1] > 55:
            vel = (vel[0], -vel[1])
        if pos[1] < 0:
            pos = (pos[0], 0)
        if pos[0] < 0:
            pos = (0, pos[1])
        return pos, vel

    def game(self, display, led, speaker, dial):
        ball_pos = (20, 30)
        ball_vel = (1, -1)
        led.set_rgb(0, 50, 0)
        score = 0
        while True:
            bar_pos = int(50 * dial.get_degree() / 100)
            ball_pos, ball_vel = self.update_screen(ball_pos, ball_vel, bar_pos
                                                    , display)
            time.sleep(0.02)
            if ball_pos[1] > 55 and (ball_pos[0] > bar_pos + 10
                                     or ball_pos[0] < bar_pos - 10):
                led.set_rgb(50, 0, 0)
                break
            elif ball_pos[1] > 55:
                speaker.set_tune(700, 100)
                time.sleep(0.1)
                speaker.set_volume(0)
                score += 1
            display.clear()
        return score
