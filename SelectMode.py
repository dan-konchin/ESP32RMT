import sys
import threading
from PyQt5.QtCore import QObject, pyqtSignal

class SelectMode(QObject):
    mode_changed = pyqtSignal(int, bool)  # mode, show

    def __init__(self):
        super().__init__()
        self._running = True
        self.last_mode = -1  # Lưu mode cuối cùng được chọn (0-8), -1 nếu chưa có

    def stop(self):
        self._running = False

    def determine_mode_yyy(self, yyy):
        if -10 < yyy < 10:
            return 0
        elif 10 <= yyy <= 90:
            return 6
        elif -90 <= yyy <= -10:
            return 8
        elif yyy > 90:
            return 2
        elif yyy < -90:
            return 4
        else:
            return 0

    def determine_mode_xxx(self, xxx):
        if -10 < xxx < 10:
            return 0
        elif 10 <= xxx <= 90:
            return 5
        elif -90 <= xxx <= -10:
            return 7
        elif xxx > 90:
            return 1
        elif xxx < -90:
            return 3
        else:
            return 0

    def process_input(self, XXX=None, YYY=None, Z=None, V=None, mode=None):
        """
        Nếu mode được truyền (từ -1 đến 8), ưu tiên dùng mode đó.
        Nếu không, xác định mode từ XXX, YYY, Z, V như trước.
        """
        if mode is not None:
            # Kiểm tra mode hợp lệ
            if not isinstance(mode, int) or mode < -1 or mode > 8:
                print(f"Error: mode phải là số nguyên từ -1 đến 8, nhận: {mode}")
                return
            # Khi mode được truyền, show = True nếu mode != -1, ngược lại show = False
            show = (mode != -1)
            self.last_mode = mode if show else self.last_mode
            self.mode_changed.emit(mode, show)
            return

        # Nếu không có mode, xử lý theo XXX, YYY, Z, V
        if not all(isinstance(x, int) for x in (XXX, YYY, Z, V)):
            print(f"Error: All inputs must be integers: {XXX}, {YYY}, {Z}, {V}")
            return
        if not (-100 <= XXX <= 100 and -100 <= YYY <= 100):
            print(f"Error: XXX and YYY must be between -100 and 100: {XXX}, {YYY}")
            return
        if Z not in (0, 1) or V not in (0, 1):
            print(f"Error: Z and V must be 0 or 1: {Z}, {V}")
            return

        show = (V == 1)

        if show:
            # So sánh giá trị tuyệt đối của XXX và YYY để xác định mode
            if abs(XXX) > abs(YYY):
                mode = self.determine_mode_xxx(XXX)
            else:
                mode = self.determine_mode_yyy(YYY)
            self.last_mode = mode
        else:
            mode = self.last_mode

        self.mode_changed.emit(mode, show)

    def run(self):
        while self._running:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) != 4:
                print(f"Invalid input line: {line}")
                continue
            try:
                XXX = int(parts[0])
                YYY = int(parts[1])
                Z = int(parts[2])
                V = int(parts[3])
            except ValueError:
                print(f"Invalid integer in line: {line}")
                continue

            self.process_input(XXX, YYY, Z, V)

    def start_in_thread(self):
        t = threading.Thread(target=self.run, daemon=True)
        t.start()
        return t