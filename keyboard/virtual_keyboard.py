# virtual_keyboard.py
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QApplication
from PyQt5.QtCore import pyqtSignal, Qt
import sys

class TvStyleVirtualKeyboard(QWidget):
    keyPressed = pyqtSignal(str)  # Phát tín hiệu khi nhấn phím

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bàn phím ảo kiểu Android TV")
        self.keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['Space', 'Backspace', 'Enter']
        ]
        self.buttons = []
        self.current_row = 0
        self.current_col = 0
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        for row_idx, row_keys in enumerate(self.keys):
            btn_row = []
            for col_idx, key in enumerate(row_keys):
                btn = QPushButton(key)
                btn.setFixedSize(60, 60)
                btn.setFocusPolicy(Qt.NoFocus)  # Tắt focus mặc định để tự quản lý
                layout.addWidget(btn, row_idx, col_idx)
                btn_row.append(btn)
            self.buttons.append(btn_row)
        self.setLayout(layout)
        self.update_focus()

    def update_focus(self):
        # Đặt style cho nút được chọn
        for r, row in enumerate(self.buttons):
            for c, btn in enumerate(row):
                if r == self.current_row and c == self.current_col:
                    btn.setStyleSheet("background-color: #3399FF; color: white; font-weight: bold;")
                else:
                    btn.setStyleSheet("")

    def keyPressEvent(self, event):
        key = event.key()
        row = self.current_row
        col = self.current_col
        max_row = len(self.buttons) - 1

        if key == Qt.Key_Up:
            if row > 0:
                new_row = row - 1
                new_col = min(col, len(self.buttons[new_row]) -1)
                self.current_row, self.current_col = new_row, new_col
                self.update_focus()
        elif key == Qt.Key_Down:
            if row < max_row:
                new_row = row + 1
                new_col = min(col, len(self.buttons[new_row]) -1)
                self.current_row, self.current_col = new_row, new_col
                self.update_focus()
        elif key == Qt.Key_Left:
            if col > 0:
                self.current_col -= 1
                self.update_focus()
        elif key == Qt.Key_Right:
            if col < len(self.buttons[row]) -1:
                self.current_col += 1
                self.update_focus()
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            selected_key = self.buttons[self.current_row][self.current_col].text()
            if selected_key == 'Space':
                selected_key = ' '
            elif selected_key == 'Backspace':
                selected_key = 'BACKSPACE'
            elif selected_key == 'Enter':
                selected_key = 'ENTER'
            print(f"Phím được chọn: {selected_key}")
            self.keyPressed.emit(selected_key)
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    vk = TvStyleVirtualKeyboard()
    vk.keyPressed.connect(lambda k: print(f"Xử lý phím: {k}"))
    vk.show()
    sys.exit(app.exec_())