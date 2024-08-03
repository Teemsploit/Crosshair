import ctypes
import json
import os
import psutil
import sys
import threading
import time
import logging

CROSSHAIR_COLOR = 0xFF0000  # rgb(255,0,0)
CROSSHAIR_SIZE = 8
VISIBLE = True
COLOR_CYCLE_KEYS = [0x2D, 0x2E]  # VK_INSERT, VK_DELETE
CONSOLE_KEY = 0x23  # VK_END
HOME_KEY = 0x24  # VK_HOME
CLOSE_KEY = 0x27  # VK_RIGHT
SW_SHOW = 5
SW_HIDE = 0
CONFIG_FILE_PATH = os.path.join(os.getenv('APPDATA'), 'crosshair_config.json')
LOG_FILE_PATH = os.path.join(os.getenv('APPDATA'), 'crosshair.log')
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class CrosshairApp:
    def __init__(self):
        self.crosshair_color = CROSSHAIR_COLOR
        self.visible = VISIBLE
        self.screen_width, self.screen_height = self.get_screen_dimensions()
        self.center_x, self.center_y = self.screen_width // 2, self.screen_height // 2

    def log_and_show_error(self, message):
        logging.error(message)
        print(message)
        user32.MessageBoxW(0, message, "Error", 1)

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as e:
            self.log_and_show_error(f"Error checking admin status: {e}")
            return False

    def request_admin(self):
        script = os.path.abspath(sys.argv[0])
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}"', None, 1)
        except Exception as e:
            self.log_and_show_error(f"Error requesting admin privileges: {e}")
            sys.exit()

    def show_elevation_message(self):
        message = (
            "This application needs administrator privileges for the following reasons:\n\n"
            "1. **Screen Drawing**: The application uses GDI (Graphics Device Interface) functions to draw directly on the screen.\n"
            "   Administrator privileges ensure that the crosshair remains visible and unaffected by other applications that might\n"
            "   override the drawing context.\n\n"
            "2. **Real-Time Priority**: The application sets its process priority to real-time to ensure the crosshair rendering is\n"
            "   smooth and responsive. This helps in reducing latency and improving the user experience.\n\n"
            "3. **Configuration Management**: The application reads and writes its configuration settings to the APPDATA directory.\n"
            "   Administrator privileges help in managing file permissions and ensuring the settings are saved correctly.\n\n"
            "4. **Input Handling**: The application monitors global key events to provide functionalities like color cycling and\n"
            "   visibility toggling. Administrator privileges allow the application to capture these events reliably.\n\n"
            "Click 'Yes' to grant administrator privileges. If you choose 'No', the application may experience errors."
        )
        result = ctypes.windll.user32.MessageBoxW(0, message, "Administrator Access Request", 4)
        if result == 6:  # IDYES
            self.request_admin()
            sys.exit()

    def set_real_time_priority(self):
        try:
            p = psutil.Process(os.getpid())
            p.nice(psutil.REALTIME_PRIORITY_CLASS)
            print("Process priority set to real-time.")
        except Exception as e:
            self.log_and_show_error(f"Error setting real-time priority: {e}")

    def load_config(self):
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                with open(CONFIG_FILE_PATH, 'r') as f:
                    config = json.load(f)
                    self.crosshair_color = config.get('color', self.crosshair_color)
                    self.visible = config.get('visible', self.visible)
                    print(f"Loaded config: Color={self.crosshair_color:#06X}, Visible={self.visible}")
            except Exception as e:
                self.log_and_show_error(f"Error loading config: {e}")

    def save_config(self):
        try:
            config = {
                'color': self.crosshair_color,
                'visible': self.visible,
            }
            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Saved config: Color={self.crosshair_color:#06X}, Visible={self.visible}")
        except Exception as e:
            self.log_and_show_error(f"Error saving config: {e}")

    def draw_crosshair(self, hdc, x, y, color):
        colorref = (color & 0xFF) | ((color & 0xFF00) << 8) | ((color & 0xFF0000) >> 8)
        for i in range(-CROSSHAIR_SIZE, CROSSHAIR_SIZE + 1):
            ctypes.windll.gdi32.SetPixel(hdc, x + i, y, colorref)
            ctypes.windll.gdi32.SetPixel(hdc, x, y + i, colorref)

    def get_screen_dimensions(self):
        width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
        return width, height

    def draw_crosshair_windows(self):
        hdc = user32.GetDC(0)
        self.draw_crosshair(hdc, self.center_x, self.center_y, self.crosshair_color)
        user32.ReleaseDC(0, hdc)

    def toggle_visibility(self):
        self.visible = not self.visible
        self.save_config()

    def cycle_color(self):
        if self.crosshair_color == 0xFF0000:  # Red
            self.crosshair_color = 0x00FF00  # Green
        elif self.crosshair_color == 0x00FF00:  # Green
            self.crosshair_color = 0x0000FF  # Blue
        elif self.crosshair_color == 0x0000FF:  # Blue
            self.crosshair_color = 0xFF0000  # Red
        self.save_config()

    def show_keybindings_message(self):
        keybindings_message = (
            "Key Bindings:\n"
            "Insert: Cycle through Red, Green, Blue\n"
            "Delete: Toggle Crosshair Visibility\n"
            "End: Open/Close Console\n"
            "Home: Reopen Key Bindings\n"
            "Right Arrow: Close Crosshair"
        )
        user32.MessageBoxW(0, keybindings_message, "Key Bindings", 1)

    def show_console(self):
        kernel32.AllocConsole()
        console_handle = kernel32.GetConsoleWindow()
        user32.ShowWindow(console_handle, SW_SHOW)
        self.save_config()
        print("Console shown.")

    def hide_console(self):
        console_handle = kernel32.GetConsoleWindow()
        user32.ShowWindow(console_handle, SW_HIDE)
        self.save_config()
        print("Console hidden.")

    def close_crosshair(self):
        self.visible = False
        self.save_config()
        print("Crosshair closed.")

    def check_toggle_key(self):
        while True:
            try:
                if user32.GetAsyncKeyState(COLOR_CYCLE_KEYS[1]) & 0x8000:  # VK_DELETE
                    self.toggle_visibility()
                    time.sleep(0.3)

                if user32.GetAsyncKeyState(CONSOLE_KEY) & 0x8000:  # VK_END
                    if kernel32.GetConsoleWindow():
                        self.hide_console()
                    else:
                        self.show_console()
                    time.sleep(0.3)

                if user32.GetAsyncKeyState(HOME_KEY) & 0x8000:  # VK_HOME
                    self.show_keybindings_message()
                    time.sleep(0.3)

                if user32.GetAsyncKeyState(CLOSE_KEY) & 0x8000:  # VK_RIGHT
                    self.close_crosshair()
                    time.sleep(0.3)
            except Exception as e:
                self.log_and_show_error(f"Error in check_toggle_key thread: {e}")

    def color_cycle_key(self):
        while True:
            try:
                if user32.GetAsyncKeyState(COLOR_CYCLE_KEYS[0]) & 0x8000:  # VK_INSERT
                    self.cycle_color()
                    time.sleep(0.3)
            except Exception as e:
                self.log_and_show_error(f"Error in color_cycle_key thread: {e}")

    def run(self):
        if not self.is_admin():
            self.show_elevation_message()

        self.set_real_time_priority()
        self.load_config()
        self.show_keybindings_message()

        toggle_thread = threading.Thread(target=self.check_toggle_key, daemon=True)
        toggle_thread.start()

        color_cycle_thread = threading.Thread(target=self.color_cycle_key, daemon=True)
        color_cycle_thread.start()

        try:
            while True:
                if self.visible:
                    try:
                        self.draw_crosshair_windows()
                    except Exception as e:
                        self.log_and_show_error(f"Error in main loop: {e}")
                time.sleep(0.005)
        except KeyboardInterrupt:
            self.save_config()
            print("Script terminated.")
            sys.exit()

if __name__ == "__main__":
    app = CrosshairApp()
    app.run()
