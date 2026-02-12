import sys
from PyQt5.QtCore import QThread, pyqtSignal

class StdinReaderThread(QThread):
    data_ready = pyqtSignal(int, int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True

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
                XXX, YYY, Z, V = map(int, parts)
            except ValueError:
                print(f"Invalid integer in line: {line}")
                continue
            self.data_ready.emit(XXX, YYY, Z, V)

    def stop(self):
        self._running = False