# mode01.py
import time
from PyQt5.QtCore import QObject, pyqtSlot, QThread
import pyautogui

class Mode01Worker(QThread):
    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        print("Mode01 bắt đầu chạy")
        while self._running:
            time.sleep(0.1)

    def stop(self):
        self._running = False
        self.wait()

class Mode01Handler(QObject):
    def __init__(self):
        super().__init__()
        self.worker = None
        self._prev_Z = None  # Lưu giá trị Z trước đó để phát hiện chuyển đổi
        self._last_press_time = 0  # Thời điểm lần cuối nhấn phím
        self._min_delay = 0.01  # Delay nhỏ nhất (nhấn nhanh nhất)
        self._max_delay = 0.2   # Delay lớn nhất (nhấn chậm nhất)

    @pyqtSlot(int, int, int, int)
    def on_input(self, XXX, YYY, Z, V):
        print(f"Mode01 nhận dữ liệu: XXX={XXX}, YYY={YYY}, Z={Z}, V={V}")

        # Giới hạn XXX và YYY trong khoảng -100 đến 100
        XXX = max(-100, min(100, XXX))
        YYY = max(-100, min(100, YYY))

        # Xử lý click chuột trái khi Z chuyển từ 1 về 0
        if self._prev_Z is not None:
            if self._prev_Z == 1 and Z == 0:
                print("Z chuyển từ 1 về 0, thực hiện click chuột trái")
                pyautogui.click(button='left')

        self._prev_Z = Z  # Cập nhật giá trị Z hiện tại

        abs_XXX = abs(XXX)
        abs_YYY = abs(YYY)

        # Nếu cả hai đều 0 thì không nhấn phím
        if abs_XXX == 0 and abs_YYY == 0:
            return

        def calc_delay(value):
            return self._max_delay - (value / 100) * (self._max_delay - self._min_delay)

        now = time.time()

        if abs_XXX >= abs_YYY:
            delay = calc_delay(abs_XXX)
            if now - self._last_press_time >= delay:
                if XXX < 0:
                    print(f"Nhấn phím trái (press), delay={delay:.3f}s")
                    pyautogui.press('left')
                elif XXX > 0:
                    print(f"Nhấn phím phải (press), delay={delay:.3f}s")
                    pyautogui.press('right')
                self._last_press_time = now
        else:
            delay = calc_delay(abs_YYY)
            if now - self._last_press_time >= delay:
                if YYY < 0:
                    print(f"Nhấn phím xuống (press), delay={delay:.3f}s")
                    pyautogui.press('down')
                elif YYY > 0:
                    print(f"Nhấn phím lên (press), delay={delay:.3f}s")
                    pyautogui.press('up')
                self._last_press_time = now

    def start(self):
        if self.worker is None:
            self.worker = Mode01Worker()
            self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()
            self.worker = None