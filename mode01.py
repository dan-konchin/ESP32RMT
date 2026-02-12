import time

_running = False

def run_mode():
    global _running
    _running = True
    print("Đang thực thi chức năng riêng cho mode 1")
    while _running:
        print("Mode 1 đang chạy...")
        time.sleep(0.1)  # ngủ 100ms để nhường CPU

def disable_mode():
    global _running
    _running = False
    print("Mode 1 disabled")