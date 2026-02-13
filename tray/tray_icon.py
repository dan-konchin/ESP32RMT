import tempfile
import os
import threading
from PIL import Image, ImageDraw
import pystray

def create_circle_icon(color, size=64):
    """
    Tạo icon hình tròn với màu sắc truyền vào.
    color: tuple (R, G, B)
    size: kích thước ảnh vuông px
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, size - 1, size - 1), fill=color + (255,))
    return image

def run_tray_icon(color=(0, 128, 255)):
    """
    Khởi chạy icon khay hệ thống với màu sắc truyền vào.
    Chạy trong thread riêng để không block luồng chính.
    """
    def on_quit(icon, item):
        icon.stop()

    def icon_thread_func():
        icon = pystray.Icon('tray_icon')
        image = create_circle_icon(color)

        with tempfile.NamedTemporaryFile(suffix='.ico', delete=False) as tmp:
            ico_path = tmp.name
            image.save(ico_path, format='ICO')

        icon.icon = Image.open(ico_path)
        icon.title = 'Circle Color Icon'
        icon.menu = pystray.Menu(
            pystray.MenuItem('Quit', on_quit)
        )
        icon.run()

        os.remove(ico_path)

    thread = threading.Thread(target=icon_thread_func, daemon=True)
    thread.start()
    return thread