import time
from PyQt5.QtCore import QObject, pyqtSlot, QThread

# Lớp worker chạy trong thread riêng, để xử lý các tác vụ của mode00
class Mode00Worker(QThread):
    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        print("Mode00 bắt đầu chạy")
        # Vòng lặp vô hạn để giữ thread sống
        while self._running:
            time.sleep(0.1)

    def stop(self):
        self._running = False
        self.wait()

# Lớp xử lý tín hiệu nhận dữ liệu
class Mode00Handler(QObject):
    def __init__(self):
        super().__init__()
        self.worker = None

    @pyqtSlot(int, int, int, int)
    def on_input(self, XXX, YYY, Z, V):
        # In ra dữ liệu nhận được
        print(f"Mode00 nhận dữ liệu: XXX={XXX}, YYY={YYY}, Z={Z}, V={V}")

    def start(self):
        # Khởi động thread xử lý
        if self.worker is None:
            self.worker = Mode00Worker()
            self.worker.start()

    def stop(self):
        # Dừng thread
        if self.worker:
            self.worker.stop()
            self.worker = None