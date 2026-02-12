import time
from PyQt5.QtCore import QObject, pyqtSlot, QThread

class Mode04Worker(QThread):
    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        print("Mode04 bắt đầu chạy")
        while self._running:
            time.sleep(0.1)

    def stop(self):
        self._running = False
        self.wait()

class Mode04Handler(QObject):
    def __init__(self):
        super().__init__()
        self.worker = None

    @pyqtSlot(int, int, int, int)
    def on_input(self, XXX, YYY, Z, V):
        print(f"Mode04 nhận dữ liệu: XXX={XXX}, YYY={YYY}, Z={Z}, V={V}")

    def start(self):
        if self.worker is None:
            self.worker = Mode04Worker()
            self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()
            self.worker = None