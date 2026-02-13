import time
from PyQt5.QtCore import QObject, pyqtSlot, QThread
import pyautogui  # pip install pyautogui

class Mode04Worker(QThread):
    def __init__(self):
        super().__init__()
        self._running = True
        self.XXX = 0
        self.YYY = 0
        self.Z = 0
        self._prev_Z = 0  # lưu trạng thái Z trước đó

    def update_values(self, XXX, YYY, Z):
        # Cập nhật giá trị XXX, YYY, Z, giới hạn trong -100 đến 100 với XXX, YYY
        self.XXX = max(-100, min(100, XXX))
        self.YYY = max(-100, min(100, YYY))

        # Kiểm tra chuyển đổi Z từ 1 về 0
        if self._prev_Z == 1 and Z == 0:
            print("Phát hiện Z chuyển từ 1 về 0, click chuột trái")
            pyautogui.click(button='left')

        self._prev_Z = Z
        self.Z = Z

    def run(self):
        print("Mode04 bắt đầu chạy")
        while self._running:
            speed_x = abs(self.XXX) / 10
            speed_y = abs(self.YYY) / 10

            if speed_x < 0.1 and speed_y < 0.1:
                time.sleep(0.1)
                continue

            if speed_y >= 0.1:
                amount_y = -speed_y if self.YYY < 0 else speed_y
                pyautogui.scroll(int(amount_y))

            if speed_x >= 0.1:
                amount_x = speed_x if self.XXX < 0 else -speed_x
                pyautogui.hscroll(int(amount_x))

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
        if self.worker:
            self.worker.update_values(XXX, YYY, Z)

    def start(self):
        if self.worker is None:
            self.worker = Mode04Worker()
            self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()
            self.worker = None