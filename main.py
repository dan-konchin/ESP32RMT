import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
from mode_widget import ModeCircleWidget
from SelectMode import SelectMode
from modes import mode_modules  # import các mode, trong đó có mode01.py, mode02.py
from stdin_reader import StdinReaderThread
import mode01
import mode02

class ModeRunnerThread(QThread):
    def __init__(self, mode_name):
        super().__init__()
        self.mode_name = mode_name
        self._running = True
        self.handler = None

    def run(self):
        if self.mode_name == 1:
            self.handler = mode01.Mode01Handler()
            self.handler.start()
            while self._running:
                self.msleep(100)
        elif self.mode_name == 2:
            self.handler = mode02.Mode02Handler()
            self.handler.start()
            while self._running:
                self.msleep(100)
        elif self.mode_name in mode_modules:
            try:
                mode_modules[self.mode_name].run_mode()
                while self._running:
                    self.msleep(100)
            except Exception as e:
                print(f"Error running mode {self.mode_name}: {e}")

    def stop(self):
        self._running = False
        if self.handler:
            self.handler.stop()
            self.handler = None
        elif self.mode_name in mode_modules and hasattr(mode_modules[self.mode_name], "disable_mode"):
            mode_modules[self.mode_name].disable_mode()

    def send_input(self, XXX, YYY, Z, V):
        if self.handler:
            self.handler.on_input(XXX, YYY, Z, V)
        else:
            print("send_input: handler chưa được khởi tạo")

    def is_ready(self):
        return self.handler is not None

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
            if selected_mode in mode_modules or selected_mode in (1, 2):
                start_mode_thread(selected_mode)
        else:
            w.hide()
            print("Circle hidden")
            # Nếu muốn dừng thread khi ẩn hình tròn, gọi stop_mode_thread()
            # stop_mode_thread()

    selector.mode_changed.connect(on_mode_changed)

    def print_mode_thread_status():
        global mode_thread
        if mode_thread is None:
            print("Chưa có thread mode nào")
        elif mode_thread.isRunning():
            print(f"Thread mode {mode_thread.mode_name} đang chạy")
        else:
            print(f"Thread mode {mode_thread.mode_name} đã dừng")

    # Khởi động mode 0 ban đầu (nếu có)
    start_mode_thread(0)

    stdin_thread = StdinReaderThread()

    def on_stdin_data(XXX, YYY, Z, V):
        global last_V, last_XXX, last_YYY

        if last_V == 1 and V == 0:
            print("V chuyển từ 1 về 0")
            last_V = V

        last_V = V

        if V == 1:
            if XXX == last_XXX and YYY == last_YYY:
                return
            last_XXX = XXX
            last_YYY = YYY

        selector.process_input(XXX, YYY, Z, V)

        if mode_thread is not None:
            if mode_thread.is_ready():
                mode_thread.send_input(XXX, YYY, Z, V)
            else:
                print("Handler chưa sẵn sàng, bỏ qua dữ liệu")
        else:
            print("Chưa có thread mode để gửi dữ liệu")

        print_mode_thread_status()

    stdin_thread.data_ready.connect(on_stdin_data)
    stdin_thread.start()

    sys.exit(app.exec_())