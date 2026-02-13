import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
from modes.mode_widget import ModeCircleWidget
from modes.SelectMode import SelectMode
from modes.modes import mode_modules  # import tất cả các mode từ modes.py
from std.stdin_reader import StdinReaderThread
from tray import tray_icon

def switch_mode(mode):
    global selected_mode, mode_thread
    if selected_mode == mode:
        print(f"Đang ở mode {mode}, không chuyển đổi.")
        return
    print(f"Chuyển từ mode {selected_mode} sang mode {mode}")
    # Dừng mode hiện tại
    if mode_thread is not None:
        mode_thread.stop()
        mode_thread.wait()
        mode_thread = None
    # Bật mode mới
    selected_mode = mode
    start_mode_thread(mode)

class ModeRunnerThread(QThread):
    def __init__(self, mode_name):
        super().__init__()
        self.mode_name = mode_name
        self._running = True
        self.handler = None

    def run(self):
        if self.mode_name in mode_modules:
            mode_module = mode_modules[self.mode_name]
            handler_class_name = None
            for attr_name in dir(mode_module):
                if attr_name.endswith("Handler"):
                    handler_class_name = attr_name
                    break
            if handler_class_name:
                handler_class = getattr(mode_module, handler_class_name)
                try:
                    self.handler = handler_class(switch_mode_callback=switch_mode)
                except TypeError:
                    self.handler = handler_class()
                self.handler.start()
                while self._running:
                    self.msleep(100)
            else:
                if hasattr(mode_module, "run_mode"):
                    try:
                        mode_module.run_mode()
                        while self._running:
                            self.msleep(100)
                    except Exception as e:
                        print(f"Error running mode {self.mode_name}: {e}")
                else:
                    print(f"Mode {self.mode_name} không có handler hoặc run_mode để chạy")
        else:
            print(f"Mode {self.mode_name} không tồn tại trong mode_modules")

    def stop(self):
        self._running = False
        if self.handler:
            self.handler.stop()
            self.handler = None
        elif self.mode_name in mode_modules:
            mode_module = mode_modules[self.mode_name]
            if hasattr(mode_module, "disable_mode"):
                mode_module.disable_mode()

    def send_input(self, XXX, YYY, Z, V):
        if self.handler:
            self.handler.on_input(XXX, YYY, Z, V)
        else:
            print("send_input: handler chưa được khởi tạo")

    def is_ready(self):
        return self.handler is not None

def open_virtual_keyboard():
    try:
        os.system("osk")  # Windows On-Screen Keyboard
        print("Bàn phím ảo đã được mở")
    except Exception as e:
        print(f"Lỗi khi mở bàn phím ảo: {e}")

if __name__ == "__main__":
    tray_icon.run_tray_icon(color=(255, 0, 0))
    app = QApplication(sys.argv)
    w = ModeCircleWidget()
    w.hide()

    selector = SelectMode()

    mode_thread = None
    last_V = None
    last_XXX = None
    last_YYY = None
    selected_mode = None
    temp_selected_mode = None  # Lưu mode đang chọn tạm thời

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
        global temp_selected_mode, mode_thread
        if show:
            # Khi vòng tròn hiện lên, dừng tất cả thread mode đang chạy
            if mode_thread is not None:
                print("Vòng tròn hiện lên, dừng thread mode hiện tại")
                mode_thread.stop()
                mode_thread.wait()
                mode_thread = None

            w.show()
            print(f"Circle shown - mode selected: {mode}")
            w.setActiveMode(mode)
            temp_selected_mode = mode  # Lưu mode đang chọn tạm thời
        else:
            w.hide()
            print("Circle hidden")

    selector.mode_changed.connect(on_mode_changed)

    def print_mode_thread_status():
        global mode_thread
        if mode_thread is None:
            print("Chưa có thread mode nào")
        elif mode_thread.isRunning():
            print(f"Thread mode {mode_thread.mode_name} đang chạy")
        else:
            print(f"Thread mode {mode_thread.mode_name} đã dừng")

    stdin_thread = StdinReaderThread()

    def on_stdin_data(XXX, YYY, Z, V):
        global last_V, last_XXX, last_YYY, selected_mode, temp_selected_mode

        if V == 1:
            if XXX == last_XXX and YYY == last_YYY:
                return
            last_XXX = XXX
            last_YYY = YYY

            selector.process_input(XXX, YYY, Z, V)

            if not w.isVisible():
                w.show()
                print("Circle shown - đang chọn mode")

        else:
            if last_V == 1 and V == 0:
                print("V chuyển từ 1 về 0 - xác nhận mode cuối cùng và chạy mode đó")
                if w.isVisible():
                    w.hide()
                    print("Circle hidden")

                if temp_selected_mode is not None:
                    if temp_selected_mode == 7:
                        print("Phát hiện mode 07, mở bàn phím ảo")
                        open_virtual_keyboard()
                        if 0 in mode_modules:
                            switch_mode(0)
                            selected_mode = 0
                        else:
                            print("Mode 00 không tồn tại")
                    else:
                        if temp_selected_mode in mode_modules:
                            switch_mode(temp_selected_mode)
                            selected_mode = temp_selected_mode
                        else:
                            print(f"Mode {temp_selected_mode} không tồn tại")
                else:
                    print("Không có mode được chọn khi V=1")
                temp_selected_mode = None
            else:
                if w.isVisible():
                    w.hide()
                    print("Circle hidden")

        last_V = V

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