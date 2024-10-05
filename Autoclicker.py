import tkinter as tk
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Key
import threading
import keyboard
import time
import pygetwindow as gw  # Library to manage windows

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")

        self.clicking = False
        self.click_position = (0, 0)
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

        # Mode Selector
        self.mode_var = tk.StringVar(value="Right Click")
        self.mode_menu = tk.OptionMenu(root, self.mode_var, "Right Click", "Enter Mode")
        self.mode_menu.pack(pady=5)

        # Program Selector Dropdown
        self.program_var = tk.StringVar(value="Select Program")
        self.program_menu = tk.OptionMenu(root, self.program_var, *self.get_open_programs())
        self.program_menu.pack(pady=5)

        # Sequence Selector Dropdown
        self.sequence_var = tk.StringVar(value="Select Sequence")
        self.sequence_menu = tk.OptionMenu(root, self.sequence_var, "Standard Click", "Custom Enter Sequence")
        self.sequence_menu.pack(pady=5)

        # Main Buttons for the GUI
        self.click_point_button = tk.Button(root, text="Click Point", command=self.get_click_position)
        self.click_point_button.pack(pady=10)

        self.start_button = tk.Button(root, text="Start", command=self.start_clicking)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_clicking)
        self.stop_button.pack(pady=10)

        # Create a separate window for the draggable button
        self.create_draggable_window()

        # Set up key bindings
        keyboard.add_hotkey('esc', self.stop_clicking)
        self.root.bind('<Return>', lambda event: self.start_clicking())

    def get_open_programs(self):
        """Returns a list of currently open window titles."""
        windows = gw.getWindowsWithTitle('')
        program_names = [win.title for win in windows if win.title.strip()]
        return program_names if program_names else ["No programs found"]

    def focus_selected_program(self):
        """Brings the selected program window to the foreground."""
        program_name = self.program_var.get()
        if program_name and program_name != "Select Program":
            windows = gw.getWindowsWithTitle(program_name)
            if windows:
                windows[0].activate()  # Bring the selected program window to the front
                print(f"Focused on {program_name}.")

    def create_draggable_window(self):
        self.draggable_window = tk.Toplevel(self.root)
        self.draggable_window.overrideredirect(True)
        self.draggable_window.geometry("100x40+500+300")
        self.draggable_window.configure(bg="lightgrey")
        self.draggable_window.lift()
        self.draggable_window.attributes('-topmost', True)
        self.draggable_button = tk.Button(self.draggable_window, text="Drag Me", bg="grey", relief='raised')
        self.draggable_button.pack(fill=tk.BOTH, expand=True)
        self.draggable_button.bind('<B1-Motion>', self.drag)

    def get_click_position(self):
        self.click_position = self.draggable_window.winfo_x(), self.draggable_window.winfo_y()
        print(f"Click position set to: {self.click_position}")

    def drag(self, event):
        x = event.x_root
        y = event.y_root
        self.draggable_window.geometry(f"+{x}+{y}")
        self.click_position = (x, y)
        print(f"Button dragged to: {self.click_position}")

    def start_clicking(self):
        if not self.clicking:
            self.clicking = True
            self.focus_selected_program()
            print(f"Starting clicks at: {self.click_position} in {self.mode_var.get()} mode with {self.sequence_var.get()} sequence.")

            # Minimize both the main window and the draggable button window
            self.root.withdraw()
            self.draggable_window.withdraw()
            self.click_thread = threading.Thread(target=self.click_loop)
            self.click_thread.start()

    def stop_clicking(self):
        self.clicking = False
        print("Clicking stopped.")
        self.root.deiconify()
        self.draggable_window.deiconify()

    def click_loop(self):
        sequence = self.sequence_var.get()
        while self.clicking:
            if sequence == "Standard Click":
                self.execute_standard_click()
            elif sequence == "Custom Enter Sequence":
                self.execute_custom_enter_sequence()
            time.sleep(0.1)  # Small delay to prevent high CPU usage

    def execute_standard_click(self):
        if self.mode_var.get() == "Right Click":
            self.mouse.position = self.click_position
            self.mouse.click(Button.right, 1)
            time.sleep(0.2)  # Standard 200ms interval
        elif self.mode_var.get() == "Enter Mode":
            self.keyboard.press(Key.enter)
            self.keyboard.release(Key.enter)
            time.sleep(0.2)

    def execute_custom_enter_sequence(self):
        # Step 1: Hit Enter
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
        time.sleep(0.15)  # Wait 100ms

        # Step 2: Hold Enter for 3 seconds
        self.keyboard.press(Key.enter)
        time.sleep(3.0)  # Hold for 3 seconds
        self.keyboard.release(Key.enter)
        time.sleep(1.2)  # Wait 200ms

        # Step 3: Hit Enter again
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
        time.sleep(0.15)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.geometry("350x300+100+100")  # Resize to fit additional elements
    root.mainloop()



