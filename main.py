import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QRect
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QPixmap, QTransform, QCursor, QPolygon
from pynput import keyboard, mouse
import math

class InputThread(QThread):
    key_pressed_signal = pyqtSignal(str)
    key_released_signal = pyqtSignal(str)
    mouse_click_signal = pyqtSignal(str, bool)
    mouse_scroll_signal = pyqtSignal(str)
    mouse_move_signal = pyqtSignal(int, int)

    def run(self):

        def on_press(key):
            try:
                self.key_pressed_signal.emit(key.char.upper())
            except AttributeError:
                if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    self.key_pressed_signal.emit("CTRL")
                elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                    self.key_pressed_signal.emit("SHIFT")
                elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                    self.key_pressed_signal.emit("ALT")
                elif key == keyboard.Key.tab:
                    self.key_pressed_signal.emit("TAB")
                elif key == keyboard.Key.space:
                    self.key_pressed_signal.emit("Space")
                elif key == keyboard.Key.caps_lock:
                    self.key_pressed_signal.emit("CAPS")

        def on_release(key):
            try:
                self.key_released_signal.emit(key.char.upper())
            except AttributeError:
                if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    self.key_released_signal.emit("CTRL")
                elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                    self.key_released_signal.emit("SHIFT")
                elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                    self.key_released_signal.emit("ALT")
                elif key == keyboard.Key.tab:
                    self.key_released_signal.emit("TAB")
                elif key == keyboard.Key.space:
                    self.key_released_signal.emit("Space")
                elif key == keyboard.Key.caps_lock:
                    self.key_released_signal.emit("CAPS")

        def on_click(x, y, button, pressed):
            if button == mouse.Button.left:
                self.mouse_click_signal.emit("left", pressed)
            elif button == mouse.Button.right:
                self.mouse_click_signal.emit("right", pressed)
            elif button == mouse.Button.middle:
                self.mouse_click_signal.emit("middle", pressed)

        def on_scroll(x, y, dx, dy):
            if dy > 0:
                self.mouse_scroll_signal.emit("scroll_up")
            else:
                self.mouse_scroll_signal.emit("scroll_down")

        def on_move(x, y):
            self.mouse_move_signal.emit(x, y)
        keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll, on_move=on_move)
        keyboard_listener.start()
        mouse_listener.start()
        keyboard_listener.join()
        mouse_listener.join()
class ArrowWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.arrow_image = QPixmap("Img/arrow.png")
        self.arrow_angle = 0
        self.arrow_x = 520
        self.arrow_y = 50

    def update_arrow(self, angle):
        """更新箭头的旋转角度"""
        self.arrow_angle = angle
        self.update()
    def paintEvent(self, event):
        """绘制旋转的箭头图片在固定位置"""
        painter = QPainter(self)
        transform = QTransform()

        pos_x = self.arrow_x
        pos_y = self.arrow_y

        image_center_x = self.arrow_image.width() / 2
        image_center_y = self.arrow_image.height() / 2

        transform.translate(pos_x, pos_y)

        transform.rotate(self.arrow_angle)

        transform.translate(-image_center_x, -image_center_y)

        painter.setTransform(transform)
        painter.drawPixmap(0, 0, self.arrow_image)

def calculate_rotation_angle(center_x, center_y, mouse_x, mouse_y):
    """根据中心点和鼠标位置计算旋转角度"""
    dx = mouse_x - center_x
    dy = mouse_y - center_y

    angle_radians = math.atan2(dy, dx)

    angle_degrees = math.degrees(angle_radians)

    if angle_degrees < 0:
        angle_degrees += 360
    return angle_degrees

class InputOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Input Overlay")

        self.setGeometry(100, 100, 800, 600)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.mouse_normal = QPixmap("Img/mouse_normal.png")
        self.mouse_left = QPixmap("Img/mouse_left.png")
        self.mouse_right = QPixmap("Img/mouse_right.png")
        self.mouse_middle = QPixmap("Img/Key_rull.png")
        self.mouse_scroll_up = QPixmap("Img/rollup.png")
        self.mouse_scroll_down = QPixmap("Img/rulldown.png")

        self.current_mouse_image = self.mouse_normal

        self.old_pos = None
        self.is_locked = False

        self.keys_pressed = set()

        self.key_positions = {
            "TAB": (20, 50, 100),
            "Q": (120, 50, 60), "W": (180, 50, 60), "E": (240, 50, 60), "R": (300, 50, 60), "T": (360, 50, 60),
            "Y": (420, 50, 60),
            "CAPS": (30, 110, 100), "A": (130, 110, 60), "S": (190, 110, 60), "D": (250, 110, 60), "F": (310, 110, 60),
            "G": (370, 110, 60), "H": (430, 110, 60),
            "SHIFT": (40, 170, 110), "Z": (150, 170, 60), "X": (210, 170, 60), "C": (270, 170, 60), "V": (330, 170, 60),
            "B": (390, 170, 60), "N": (450, 170, 60),
            "CTRL": (40, 230, 80), "Win": (120, 230, 60), "ALT": (180, 230, 50), "Space": (230, 230, 300)
        }

        self.arrow_widget = ArrowWidget(self)
        self.arrow_widget.setGeometry(0, 0, self.width(), self.height())  # 设置 ArrowWidget 尺寸

        layout = QVBoxLayout(self)
        layout.addWidget(self.arrow_widget)

        self.input_thread = InputThread()
        self.input_thread.key_pressed_signal.connect(self.on_key_press)
        self.input_thread.key_released_signal.connect(self.on_key_release)
        self.input_thread.mouse_click_signal.connect(self.on_mouse_click)
        self.input_thread.mouse_scroll_signal.connect(self.on_mouse_scroll)
        self.input_thread.mouse_move_signal.connect(self.on_mouse_move)

        self.input_thread.start()

    def on_key_press(self, key):
        """处理键盘按下事件"""
        if key in self.key_positions:
            self.keys_pressed.add(key)
        self.update()

    def on_key_release(self, key):
        """处理键盘松开事件"""
        if key in self.key_positions:
            self.keys_pressed.discard(key)
        self.update()

    def on_mouse_click(self, button, pressed):
        """处理鼠标点击事件"""
        if button == "left":
            self.left_mouse_pressed = pressed
            self.current_mouse_image = self.mouse_left if pressed else self.mouse_normal
        elif button == "right":
            self.right_mouse_pressed = pressed
            self.current_mouse_image = self.mouse_right if pressed else self.mouse_normal

        if button == "right" and not pressed:  # 释放右键时切换锁定状态
            if self.rect().contains(self.mapFromGlobal(QCursor.pos())):  # 检查鼠标是否在窗口内
                self.is_locked = not self.is_locked
                self.show_lock_status()
        self.update()

    def on_mouse_scroll(self, direction):
        """处理鼠标滚轮事件"""
        if direction == "scroll_up":
            self.current_mouse_image = self.mouse_scroll_up
        else:
            self.current_mouse_image = self.mouse_scroll_down
        self.update()

    def on_mouse_move(self, x, y):
        """处理鼠标移动事件，更新箭头角度"""
        # 使用屏幕中心点计算旋转角度
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        center_x = screen_geometry.width() // 2
        center_y = screen_geometry.height() // 2

        angle = calculate_rotation_angle(center_x, center_y, x, y)
        self.arrow_widget.update_arrow(angle)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.is_locked:
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None
        elif event.button() == Qt.RightButton:
            self.is_locked = not self.is_locked
            self.show_lock_status()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None and not self.is_locked:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def show_lock_status(self):
        if self.is_locked:
            msg = "窗口已锁定"
        else:
            msg = "窗口已解锁"

        QMessageBox.information(self, "状态", msg, QMessageBox.Ok)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.drawKeyboardLayout(painter)
        for key in self.keys_pressed:
            if key in self.key_positions:
                x, y, width = self.key_positions[key]
                self.drawKey(painter, key, x, y, width, pressed=True)

        self.drawMouseImage(painter)

    def drawKeyboardLayout(self, painter):
        for label, (x, y, width) in self.key_positions.items():
            self.drawKey(painter, label, x, y, width)

    def drawKey(self, painter, label, x, y, width, pressed=False):
        height = 60
        skew = 15  # 倾斜程度

        points = [
            QPoint(x + skew, y),
            QPoint(x + width + skew, y),
            QPoint(x + width - skew, y + height),
            QPoint(x - skew, y + height)
        ]

        polygon = QPolygon(points)

        if pressed:
            painter.setBrush(QColor(255, 255, 0, 150))
        else:
            painter.setBrush(QColor(255, 255, 255, 30))

        painter.setPen(QPen(Qt.darkCyan, 2))
        painter.drawPolygon(polygon)

        font = QFont("Arial", 14, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(Qt.white, 2))


        text_rect = QRect(x, y, width, height)
        painter.drawText(text_rect, Qt.AlignCenter, label)

    def drawMouseImage(self, painter):
        mouse_x, mouse_y = 550, 80
        scaled_mouse_image = self.current_mouse_image.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(mouse_x, mouse_y, scaled_mouse_image)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InputOverlay()
    window.show()
    sys.exit(app.exec_())
