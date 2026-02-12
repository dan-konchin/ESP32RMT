import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from mode_widget import ModeCircleWidget
from SelectMode import SelectMode
from modes import mode_modules  # import các mode, trong đó có mode01.py

class ModeRunnerThread(QThread):
    def __init__(self, mode_name):
        super().__init__()
        self.mode_name = mode_name
        self._running = True

    def run(self):
        if self.mode_name in mode_modules:
            try:
                mode_modules[self.mode_name].run_mode()
                while self._running:
                    self.msleep(100)
            except Exception as e:
                print(f"Error running mode {self.mode_name}: {e}")

    def stop(self):
        self._running = False
        if self.mode_name in mode_modules and hasattr(mode_modules[self.mode_name], "disable_mode"):
            mode_modules[self.mode_name].disable_mode()

class StdinReaderThread(QThread):
    line_read = pyqtSignal(str)

    def run(self):
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            self.line_read.emit(line.strip())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ModeCircleWidget()
    w.hide()

    selector = SelectMode()

    mode_thread = None
    last_V = None
    last_XXX = None
    last_YYY = None
    selected_mode = None

    def start_mode_thread(mode):
        global mode_thread
        if mode_thread is not None:
            mode_thread.stop()
            mode_thread.wait()
            mode_thread = None
        mode_thread = ModeRunnerThread(mode)
        mode_thread.start()
        print(f"Started mode thread for mode {mode}")

    def stop_mode_thread():
        global mode_thread
        if mode_thread is not None:
            mode_thread.stop()
            mode_thread.wait()
            mode_thread = None
            print("Stopped mode thread")

    def on_mode_changed(mode, show):
        global selected_mode
        if show:
            stop_mode_thread()
            w.show()
            print(f"Circle shown - mode selected: {mode}")
            w.setActiveMode(mode)
            selected_mode = mode
        else:
            w.hide()
            print("Circle hidden")
            if selected_mode in mode_modules:
                start_mode_thread(selected_mode)
            else:
                print(f"Mode {selected_mode} not found, no thread started")

    selector.mode_changed.connect(on_mode_changed)

    def print_mode_thread_status():
        global mode_thread
        if mode_thread is None:
            print("Chưa có thread mode nào")
        elif mode_thread.isRunning():
            print(f"Thread mode {mode_thread.mode_name} đang chạy")
        else:
            print(f"Thread mode {mode_thread.mode_name} đã dừng")

    start_mode_thread(0)

    stdin_thread = StdinReaderThread()

    def on_stdin_line(line):
        global last_V, last_XXX, last_YYY
        parts = line.split(",")
        if len(parts) != 4:
            print(f"Invalid input line: {line}")
            return
        try:
            XXX = int(parts[0])
            YYY = int(parts[1])
            Z = int(parts[2])
            V = int(parts[3])
        except ValueError:
            print(f"Invalid integer in line: {line}")
            return

        if last_V == 1 and V == 0:
            print("V chuyển từ 1 về 0, chạy mode mới nếu có và ẩn hình tròn")
            if selected_mode in mode_modules:
                start_mode_thread(selected_mode)
            else:
                print(f"Mode {selected_mode} không hợp lệ hoặc chưa chọn")
            w.hide()
            last_V = V
            return

        if V == 0:
            last_V = V
            return

        if V == 1:
            if XXX == last_XXX and YYY == last_YYY:
                return
            last_XXX = XXX
            last_YYY = YYY

        last_V = V

        selector.process_input(XXX, YYY, Z, V)
        print_mode_thread_status()

    stdin_thread.line_read.connect(on_stdin_line)
    stdin_thread.start()

    sys.exit(app.exec_())