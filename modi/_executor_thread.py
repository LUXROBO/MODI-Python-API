import threading
import setproctitle

from modi._executor_task import ExecutorTask


class ExecutorThread(threading.Thread):
    """
    :param queue serial_write_q: Inter-process queue for serial writing message
    :param queue json_recv_q: Inter-process queue for receiving json message
    :param dict() module_ids: dict() of module_id : ['timestamp', 'uuid']
    :param list() modules: list() of module instance
    """

    def __init__(self, modules, module_ids, topology_data,
                 serial_read_q, serial_write_q):
        super().__init__()
        self.__exe_task = ExecutorTask(
            modules, module_ids, topology_data, serial_read_q, serial_write_q)

        setproctitle.setproctitle('pymodi-executor')

    def run(self):
        """ Run executor task
        """

        self.__exe_task.init_modules()
        while 1:
            self.__exe_task.run(delay=0.001)
