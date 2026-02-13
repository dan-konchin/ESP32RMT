# mode05.py
import time
from PyQt5.QtCore import QObject, pyqtSlot, QThread
import pyautogui

class Mode05Worker(QThread):
    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        print("Mode05 bắt đầu chạy")
        while self._running:
            time.sleep(0.1)

    def stop(self):
        self._running = False
        self.wait()

class Mode05Handler(QObject):
    def __init__(self):
        super().__init__()
        self.worker = None
        self._prev_Z = None
        self._last_action_time = 0
        self._action_interval = 0.1  # khoảng thời gian giữa các lần gửi phím (giây)

        self._speed = 1.0
        self._min_speed = 0.25
        self._max_speed = 4.0

        self._volume = 50
        self._min_volume = 0
        self._max_volume = 100

        self._z_transition_times = []  # lưu thời điểm Z chuyển từ 1 về 0

    @pyqtSlot(int, int, int, int)
    def on_input(self, XXX, YYY, Z, V):
        print(f"Mode05 nhận dữ liệu: XXX={XXX}, YYY={YYY}, Z={Z}, V={V}")

        # Giới hạn XXX và YYY trong khoảng -100 đến 100
        XXX = max(-100, min(100, XXX))
        YYY = max(-100, min(100, YYY))

        now = time.time()

        # Xử lý play/pause và full màn hình khi Z chuyển từ 1 về 0
        if self._prev_Z is not None:
            if self._prev_Z == 1 and Z == 0:
                print("Z chuyển từ 1 về 0, toggle play/pause")
                pyautogui.press('space')

                # Ghi lại thời điểm chuyển đổi Z
                self._z_transition_times.append(now)

                # Loại bỏ các lần chuyển đổi cũ hơn 0.7 giây
                self._z_transition_times = [t for t in self._z_transition_times if now - t <= 0.7]

                # Nếu có 2 lần chuyển đổi trong 0.7 giây, toggle full màn hình
                if len(self._z_transition_times) >= 2:
                    print("Phát hiện 2 lần Z chuyển từ 1 về 0 trong 0.7s, toggle full màn hình")
                    pyautogui.press('f')
                    self._z_transition_times.clear()  # reset bộ đếm

        self._prev_Z = Z

        abs_XXX = abs(XXX)
        abs_YYY = abs(YYY)

        # Nếu cả hai đều 0 thì không làm gì
        if abs_XXX == 0 and abs_YYY == 0:
            return

        # Giới hạn tần suất gửi phím
        if now - self._last_action_time < self._action_interval:
            return

        def calc_delay(value):
            return self._max_speed - (value / 100) * (self._max_speed - self._min_speed)

        # So sánh abs để quyết định xử lý theo XXX hay YYY
        if abs_XXX >= abs_YYY:
            # Xử lý tốc độ phát theo XXX
            speed_change = (abs_XXX / 100) * 0.1  # mỗi lần thay đổi 0.1x tốc độ theo giá trị
            if XXX > 0:
                new_speed = min(self._speed + speed_change, self._max_speed)
            else:
                new_speed = max(self._speed - speed_change, self._min_speed)

            if abs(new_speed - self._speed) >= 0.01:
                self._speed = new_speed
                print(f"Điều chỉnh tốc độ phát VLC: {self._speed:.2f}x")
                if XXX > 0:
                    pyautogui.press(']')
                else:
                    pyautogui.press('[')
                self._last_action_time = now

        else:
            # Xử lý âm lượng theo YYY
            volume_change = int((abs_YYY / 100) * 5)
            if volume_change == 0:
                volume_change = 1

            if YYY > 0:
                new_volume = min(self._volume + volume_change, self._max_volume)
            else:
                new_volume = max(self._volume - volume_change, self._min_volume)

            if new_volume != self._volume:
                self._volume = new_volume
                print(f"Điều chỉnh âm lượng VLC: {self._volume}")
                if YYY > 0:
                    pyautogui.keyDown('ctrl')
                    pyautogui.press('up')
                    pyautogui.keyUp('ctrl')
                else:
                    pyautogui.keyDown('ctrl')
                    pyautogui.press('down')
                    pyautogui.keyUp('ctrl')
                self._last_action_time = now

    def start(self):
        if self.worker is None:
            self.worker = Mode05Worker()
            self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()
            self.worker = None