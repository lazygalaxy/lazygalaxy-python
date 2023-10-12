import win32gui

def callback(hwnd, extra):
    if win32gui.IsWindowVisible(hwnd):
        print(f"window text: '{win32gui.GetWindowText(hwnd)}'")

win32gui.EnumWindows(callback, None)