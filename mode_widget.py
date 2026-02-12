from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QRadialGradient
from PyQt5.QtCore import Qt, QRectF, QPoint, QPropertyAnimation, pyqtProperty, QEasingCurve
import math

class ModeCircleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hình tròn 9 mode: 4 ngoài, 4 trong, 1 trung tâm")

        self.base_radius = 100
        self.scale_factor = 1.5
        self.radius_outer = int(self.base_radius * self.scale_factor)  # bán kính vòng ngoài
        self.radius_inner = int(self.radius_outer * 0.6)  # bán kính vòng trong nhỏ hơn
        self.radius_center = int(self.radius_outer * 0.3)  # bán kính trung tâm nhỏ nhất

        self.active_mode = None
        self.highlight_states = {mode: False for mode in range(9)}

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.margin_blur_max = 120
        diameter = self.radius_outer * 2 + self.margin_blur_max * 2
        self.resize(diameter, diameter)

        region = QRegion(self.rect(), QRegion.Ellipse)
        self.setMask(region)

        # Định nghĩa các phần vòng ngoài (mode 1-4)
        self.parts_outer = {
            1: (45 * 16, 90 * 16),
            2: (315 * 16, 90 * 16),
            3: (225 * 16, 90 * 16),
            4: (135 * 16, 90 * 16),
        }

        # Định nghĩa các phần vòng trong (mode 5-8)
        self.parts_inner = {
            5: (45 * 16, 90 * 16),
            6: (315 * 16, 90 * 16),
            7: (225 * 16, 90 * 16),
            8: (135 * 16, 90 * 16),
        }

        # Animation variables
        self._scale = 1.0
        self._blur_margin = 0.0

        self.anim_scale = QPropertyAnimation(self, b"scale")
        self.anim_scale.setDuration(300)  # 300ms
        self.anim_scale.setEasingCurve(QEasingCurve.OutCubic)

        self.anim_blur = QPropertyAnimation(self, b"blur_margin")
        self.anim_blur.setDuration(300)
        self.anim_blur.setEasingCurve(QEasingCurve.OutCubic)

    # scale property
    def getScale(self):
        return self._scale

    def setScale(self, value):
        self._scale = value
        self.update()

    scale = pyqtProperty(float, fget=getScale, fset=setScale)

    # blur_margin property
    def getBlurMargin(self):
        return self._blur_margin

    def setBlurMargin(self, value):
        self._blur_margin = value
        self.update()

    blur_margin = pyqtProperty(float, fget=getBlurMargin, fset=setBlurMargin)

    def setActiveMode(self, mode):
        if mode in range(0, 9):
            self.active_mode = mode
            # Reset tất cả highlight
            for m in self.highlight_states:
                self.highlight_states[m] = False
            # Set highlight cho mode active
            self.highlight_states[mode] = True

            # Nếu mode 3 active, gỡ highlight mode 7 và 0
            if mode == 3:
                self.highlight_states[7] = False
                self.highlight_states[0] = False
        else:
            self.active_mode = None
            for m in self.highlight_states:
                self.highlight_states[m] = False

        # Bắt đầu animation: phóng to rồi thu nhỏ, đồng thời tăng giảm blur
        self.anim_scale.stop()
        self.anim_blur.stop()

        self.anim_scale.setStartValue(1.0)
        self.anim_scale.setKeyValueAt(0.5, 1.2)  # phóng to 1.2 lần
        self.anim_scale.setEndValue(1.0)

        self.anim_blur.setStartValue(0.0)
        self.anim_blur.setKeyValueAt(0.5, self.margin_blur_max)
        self.anim_blur.setEndValue(0.0)

        self.anim_scale.start()
        self.anim_blur.start()

    def is_mode_highlighted(self, mode):
        return self.highlight_states.get(mode, False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = QPoint(self.width() // 2, self.height() // 2)

        # Tính bán kính theo scale animation
        radius_outer_scaled = self.radius_outer * self._scale
        radius_inner_scaled = self.radius_inner * self._scale
        radius_center_scaled = self.radius_center * self._scale

        rect_outer = QRectF(center.x() - radius_outer_scaled,
                            center.y() - radius_outer_scaled,
                            radius_outer_scaled * 2,
                            radius_outer_scaled * 2)

        rect_inner = QRectF(center.x() - radius_inner_scaled,
                            center.y() - radius_inner_scaled,
                            radius_inner_scaled * 2,
                            radius_inner_scaled * 2)

        rect_center = QRectF(center.x() - radius_center_scaled,
                             center.y() - radius_center_scaled,
                             radius_center_scaled * 2,
                             radius_center_scaled * 2)

        # Vẽ nền vòng ngoài
        gradient_outer = QRadialGradient(center, radius_outer_scaled)
        gradient_outer.setColorAt(0.0, QColor(100, 100, 100, 50))
        gradient_outer.setColorAt(1.0, QColor(100, 100, 100, 10))
        painter.setBrush(QBrush(gradient_outer))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect_outer)

        # Vẽ nền vòng trong
        gradient_inner = QRadialGradient(center, radius_inner_scaled)
        gradient_inner.setColorAt(0.0, QColor(120, 120, 120, 40))
        gradient_inner.setColorAt(1.0, QColor(120, 120, 120, 8))
        painter.setBrush(QBrush(gradient_inner))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect_inner)

        # Vẽ nền trung tâm
        gradient_center = QRadialGradient(center, radius_center_scaled)
        gradient_center.setColorAt(0.0, QColor(150, 150, 150, 80))
        gradient_center.setColorAt(1.0, QColor(150, 150, 150, 20))
        painter.setBrush(QBrush(gradient_center))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect_center)

        def convert_angle(angle_16):
            deg = angle_16 / 16
            deg = (360 - deg) % 360
            return int(deg * 16)

        parts_outer_converted = {k: (convert_angle(v[0]), v[1]) for k, v in self.parts_outer.items()}
        parts_inner_converted = {k: (convert_angle(v[0]), v[1]) for k, v in self.parts_inner.items()}

        alpha_base_outer = int(255 * 0.05)
        alpha_active_outer = int(255 * 0.07)
        alpha_base_inner = int(255 * 0.04)
        alpha_active_inner = int(255 * 0.06)
        alpha_center_base = int(255 * 0.1)
        alpha_center_active = int(255 * 0.15)

        base_color_outer = QColor(100, 100, 100, alpha_base_outer)
        highlight_color_outer = QColor(255, 255, 0, alpha_active_outer)

        base_color_inner = QColor(120, 120, 120, alpha_base_inner)
        highlight_color_inner = QColor(255, 165, 0, alpha_active_inner)

        base_color_center = QColor(150, 150, 150, alpha_center_base)
        highlight_color_center = QColor(255, 255, 0, alpha_center_active)  # màu vàng giống vòng ngoài

        max_blur_layers = 30

        margin_blur = self._blur_margin

        # Vẽ vòng ngoài (mode 1-4)
        for mode, (start_angle, span_angle) in parts_outer_converted.items():
            is_active_outer = self.is_mode_highlighted(mode)
            if is_active_outer:
                painter.setBrush(QBrush(highlight_color_outer))
                painter.setPen(Qt.NoPen)
                painter.drawPie(rect_outer, start_angle, span_angle)

                for i in range(1, max_blur_layers + 1):
                    t = i / (max_blur_layers + 1)
                    alpha = int(alpha_active_outer * (1 - t)**2)
                    if alpha <= 0:
                        continue
                    color = QColor(255, 255, 0, alpha)
                    painter.setBrush(QBrush(color))
                    painter.setPen(Qt.NoPen)
                    margin = margin_blur * t
                    rect_blur = QRectF(rect_outer.x() - margin, rect_outer.y() - margin,
                                       rect_outer.width() + margin * 2, rect_outer.height() + margin * 2)
                    painter.drawPie(rect_blur, start_angle, span_angle)
            else:
                painter.setBrush(QBrush(base_color_outer))
                painter.setPen(Qt.NoPen)
                painter.drawPie(rect_outer, start_angle, span_angle)

                for i in range(1, max_blur_layers + 1):
                    t = i / (max_blur_layers + 1)
                    alpha = int(alpha_base_outer * (1 - t)**1.5)
                    if alpha <= 0:
                        continue
                    color = QColor(100, 100, 100, alpha)
                    painter.setBrush(QBrush(color))
                    painter.setPen(Qt.NoPen)
                    margin = margin_blur * t
                    rect_blur = QRectF(rect_outer.x() - margin, rect_outer.y() - margin,
                                       rect_outer.width() + margin * 2, rect_outer.height() + margin * 2)
                    painter.drawPie(rect_blur, start_angle, span_angle)

        # Vẽ vòng trong (mode 5-8)
        for mode, (start_angle, span_angle) in parts_inner_converted.items():
            is_active_inner = self.is_mode_highlighted(mode)
            if is_active_inner:
                painter.setBrush(QBrush(highlight_color_inner))
                painter.setPen(Qt.NoPen)
                painter.drawPie(rect_inner, start_angle, span_angle)

                for i in range(1, max_blur_layers + 1):
                    t = i / (max_blur_layers + 1)
                    alpha = int(alpha_active_inner * (1 - t)**2)
                    if alpha <= 0:
                        continue
                    color = QColor(255, 165, 0, alpha)
                    painter.setBrush(QBrush(color))
                    painter.setPen(Qt.NoPen)
                    margin = margin_blur * t * 0.5
                    rect_blur = QRectF(rect_inner.x() - margin, rect_inner.y() - margin,
                                       rect_inner.width() + margin * 2, rect_inner.height() + margin * 2)
                    painter.drawPie(rect_blur, start_angle, span_angle)
            else:
                painter.setBrush(QBrush(base_color_inner))
                painter.setPen(Qt.NoPen)
                painter.drawPie(rect_inner, start_angle, span_angle)

                for i in range(1, max_blur_layers + 1):
                    t = i / (max_blur_layers + 1)
                    alpha = int(alpha_base_inner * (1 - t)**1.5)
                    if alpha <= 0:
                        continue
                    color = QColor(120, 120, 120, alpha)
                    painter.setBrush(QBrush(color))
                    painter.setPen(Qt.NoPen)
                    margin = margin_blur * t * 0.5
                    rect_blur = QRectF(rect_inner.x() - margin, rect_inner.y() - margin,
                                       rect_inner.width() + margin * 2, rect_inner.height() + margin * 2)
                    painter.drawPie(rect_blur, start_angle, span_angle)

        # Vẽ phần trung tâm (mode 0)
        if self.is_mode_highlighted(0):
            painter.setBrush(QBrush(highlight_color_center))
        else:
            painter.setBrush(QBrush(base_color_center))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect_center)

        # Hàm lấy màu text theo trạng thái highlight
        def get_text_color(mode):
            if self.is_mode_highlighted(mode):
                if mode == 0:
                    return QColor(255, 255, 0, 255)  # vàng đậm cho trung tâm active
                elif 1 <= mode <= 4:
                    return QColor(255, 255, 0, 255)  # vàng đậm cho vòng ngoài
                elif 5 <= mode <= 8:
                    return QColor(255, 165, 0, 255)  # cam đậm cho vòng trong
                else:
                    return QColor(255, 255, 255, 255)
            else:
                return QColor(255, 255, 255, 200)  # trắng mờ cho text không active

        parts_outer_text = {
            1: "1",
            2: "2",
            3: "3",
            4: "4",
        }

        parts_inner_text = {
            5: "5",
            6: "6",
            7: "7",
            8: "8",
        }

        def angle16_to_deg(angle16):
            return angle16 / 16

        # Vẽ text vòng ngoài (text thẳng)
        for mode, (start_angle16, span_angle16) in self.parts_outer.items():
            start_deg = (360 - angle16_to_deg(start_angle16)) % 360
            text = parts_outer_text.get(mode, "")
            color = get_text_color(mode)
            font_size = 22 if self.is_mode_highlighted(mode) else 12

            # Tính vị trí text trên vòng tròn
            angle_rad = math.radians(start_deg + span_angle16 / 32)  # trung tâm cung
            radius_text = radius_outer_scaled * 0.7
            x = center.x() + radius_text * math.cos(angle_rad)
            y = center.y() - radius_text * math.sin(angle_rad)

            font = painter.font()
            font.setBold(True)
            font.setPointSize(font_size)
            painter.setFont(font)
            painter.setPen(color)

            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(text)
            text_height = metrics.height()

            painter.drawText(int(x - text_width / 2), int(y + text_height / 4), text)

        # Vẽ text vòng trong (text thẳng)
        for mode, (start_angle16, span_angle16) in self.parts_inner.items():
            start_deg = (360 - angle16_to_deg(start_angle16)) % 360
            text = parts_inner_text.get(mode, "")
            color = get_text_color(mode)
            font_size = 22 if self.is_mode_highlighted(mode) else 12

            angle_rad = math.radians(start_deg + span_angle16 / 32)
            radius_text = radius_inner_scaled * 0.7
            x = center.x() + radius_text * math.cos(angle_rad)
            y = center.y() - radius_text * math.sin(angle_rad)

            font = painter.font()
            font.setBold(True)
            font.setPointSize(font_size)
            painter.setFont(font)
            painter.setPen(color)

            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(text)
            text_height = metrics.height()

            painter.drawText(int(x - text_width / 2), int(y + text_height / 4), text)

        # Vẽ text trung tâm
        center_text = "0"
        color_center = get_text_color(0)
        font = painter.font()
        font.setBold(True)
        font.setPointSize(22 if self.is_mode_highlighted(0) else 12)
        painter.setFont(font)
        painter.setPen(color_center)
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(center_text)
        text_height = metrics.height()
        painter.drawText(center.x() - text_width // 2, center.y() + text_height // 4, center_text)