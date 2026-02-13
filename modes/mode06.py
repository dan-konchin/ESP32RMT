import time
from PyQt5.QtCore import QObject, pyqtSlot, QThread

class Mode06Worker(QThread):
    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        print("Mode06 bắt đầu chạy")
        while self._running:
            time.sleep(0.1)

    def stop(self):
        self._running = False
        self.wait()

class Mode06Handler(QObject):
    def __init__(self):
        super().__init__()
        self.worker = None

    @pyqtSlot(int, int, int, int)
    def on_input(self, XXX, YYY, Z, V):
        print(f"Mode06 nhận dữ liệu: XXX={XXX}, YYY={YYY}, Z={Z}, V={V}")

    def start(self):
        if self.worker is None:
            self.worker = Mode06Worker()
            self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()
            self.worker = None