"""
Kernel Loop Service Wrapper
Location: senti_os/kernel/kernel_loop_service.py

Naloga:
- pretvori KernelLoop v OS Service
- omogoča Service Managerju upravljanje Kernel Loop ciklov
"""

import threading
from senti_os.kernel.kernel_loop import KernelLoop
from senti_os.kernel.core import SentiKernel
from senti_core.system.logger import SentiLogger


class KernelLoopService:
    """
    OS Service wrapper za KernelLoop.
    """

    def __init__(self, kernel: SentiKernel, cycles: int = 999999, tick_interval: float = 1.0):
        self.kernel = kernel
        self.cycles = cycles
        self.tick_interval = tick_interval

        self.loop = KernelLoop(kernel=self.kernel, tick_interval=tick_interval)
        self.thread = None
        self.running = False
        self.logger = SentiLogger()

        self.logger.log("info", "KernelLoopService created.")

    # =====================================================
    # SERVICE START
    # =====================================================

    def start(self):
        """
        Zažene KernelLoop v varni niti.
        """
        if self.running:
            self.logger.log("warning", "KernelLoopService already running.")
            return False

        def loop_runner():
            self.logger.log("info", "KernelLoopService thread started.")
            self.loop.run(cycles=self.cycles)
            self.running = False
            self.logger.log("info", "KernelLoopService thread finished.")

        self.thread = threading.Thread(target=loop_runner, daemon=True)
        self.thread.start()

        self.running = True
        self.logger.log("info", "KernelLoopService started.")
        return True

    # =====================================================
    # SERVICE STOP
    # =====================================================

    def stop(self):
        """
        Ustavi KernelLoop tako, da prekine dodatne cikle.
        """
        if not self.running:
            self.logger.log("warning", "KernelLoopService not running.")
            return False

        self.loop.cycles = 0  # prekini nadaljnje cikle
        self.running = False

        self.logger.log("info", "KernelLoopService stopped.")
        return True

    # =====================================================
    # SERVICE STATUS
    # =====================================================

    def status(self):
        """
        Vrne stanje servisne niti.
        """
        return {
            "service": "kernel_loop",
            "running": self.running,
            "thread_alive": self.thread.is_alive() if self.thread else False,
            "tick_interval": self.tick_interval,
        }
