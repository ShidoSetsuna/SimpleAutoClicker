import tkinter as tk
from tkinter import ttk
import pyautogui
import threading
import time
import win32gui  # For handling window focusing
import keyboard  # Global keyboard listener (requires `pip install keyboard`)

# Global variables to track buttons, click points, and minimized state
drag_buttons = []
click_positions = []
drag_windows = []

# To track the auto-clicker state
auto_clicker_running = threading.Event()

# Function to list currently open windows
def get_open_windows():
    windows = []
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            windows.append(win32gui.GetWindowText(hwnd))
    win32gui.EnumWindows(callback, None)
    return [win for win in windows if win.strip()]

# Function to focus on a specific window
def focus_on_window(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        win32gui.SetForegroundWindow(hwnd)

# Function to handle clicks based on the selected mode
def perform_click(mode, x, y, sequence=None):
    if sequence:
        for action in sequence:
            if action['type'] == 'click':
                pyautogui.click(x, y) if mode == 'Left Click' else pyautogui.rightClick(x, y)
            elif action['type'] == 'press':
                pyautogui.press(action['key'])
            elif action['type'] == 'hold':
                pyautogui.keyDown(action['key'])
                time.sleep(action['duration'])
                pyautogui.keyUp(action['key'])
            time.sleep(action['wait'])
    else:
        if mode == "Right Click":
            pyautogui.rightClick(x, y)
        elif mode == "Left Click":
            pyautogui.leftClick(x, y)
        elif mode == "Enter Mode":
            pyautogui.press('enter')

# Function to start the auto-clicker with sequence support
def start_auto_clicker():
    mode = mode_var.get()
    interval = 0.2  # Fixed interval between clicks for now

    # Retrieve the selected sequence (if any)
    selected_sequence = sequences_var.get()
    sequence = predefined_sequences.get(selected_sequence, None)

    # Focus on the selected program window
    selected_program = window_var.get()
    if selected_program:
        focus_on_window(selected_program)

    # Hide all drag buttons when the auto-clicker starts
    for button_window in drag_windows:
        button_window.withdraw()

    # Minimize the main window
    root.iconify()

    # Define the click loop
    def click_loop():
        while auto_clicker_running.is_set():
            for index, (x, y) in enumerate(click_positions):
                perform_click(mode, x, y, sequence)
                time.sleep(interval)

    # Start the auto-clicker thread
    auto_clicker_running.set()
    threading.Thread(target=click_loop).start()

# Function to stop the auto-clicker
def stop_auto_clicker():
    auto_clicker_running.clear()

    # Restore the drag buttons
    for button_window in drag_windows:
        button_window.deiconify()

    # Restore the main window
    root.deiconify()

# Function to create a frameless draggable window for each button
def create_floating_button(button_name):
    button_window = tk.Toplevel()  # Create a new top-level window for each button
    button_window.overrideredirect(True)  # Remove the window's top bar
    button_window.geometry("100x50+50+50")  # Set initial size and position
    button_window.wm_attributes("-topmost", True)  # Keep the window on top

    # Create a draggable button inside the frameless window
    drag_button = tk.Button(button_window, text=button_name, bg="lightblue")
    drag_button.pack(expand=True, fill='both')

    # Track position updates in `click_positions`
    drag_windows.append(button_window)
    click_positions.append((button_window.winfo_x(), button_window.winfo_y()))

    # Function to handle window dragging
    def start_drag(event):
        button_window._drag_start_x = event.x
        button_window._drag_start_y = event.y

    def do_drag(event):
        # Calculate the new position
        x = event.x_root - button_window._drag_start_x
        y = event.y_root - button_window._drag_start_y
        button_window.geometry(f"+{x}+{y}")

        # Update click position for this button
        index = drag_windows.index(button_window)
        click_positions[index] = (x, y)

    # Function to delete button on right-click
    def delete_button(event):
        index = drag_windows.index(button_window)
        drag_windows.pop(index)
        click_positions.pop(index)
        button_window.destroy()

    # Bind mouse events for dragging and deletion
    drag_button.bind("<ButtonPress-1>", start_drag)
    drag_button.bind("<B1-Motion>", do_drag)
    drag_button.bind("<Button-3>", delete_button)  # Right-click to delete

# Function to add a new floating "Drag Me" button
def add_click_button():
    button_name = f"Drag Me#{len(drag_windows) + 1}"
    create_floating_button(button_name)

# Main Application Window
root = tk.Tk()
root.title("Auto Clicker")
root.geometry("500x400")

# Dropdown menu to select click mode
mode_var = tk.StringVar(value="Right Click")
mode_label = tk.Label(root, text="Select Mode:")
mode_label.pack()
mode_dropdown = ttk.Combobox(root, textvariable=mode_var, values=["Right Click", "Left Click", "Enter Mode"])
mode_dropdown.pack()

# Dropdown menu for selecting active program
window_var = tk.StringVar(value="")
window_label = tk.Label(root, text="Select Window to Focus On:")
window_label.pack()
window_dropdown = ttk.Combobox(root, textvariable=window_var, values=get_open_windows())
window_dropdown.pack()

# Dropdown menu for selecting a sequence
sequences_var = tk.StringVar(value="Default Sequence")
sequence_label = tk.Label(root, text="Select Sequence:")
sequence_label.pack()
sequence_dropdown = ttk.Combobox(root, textvariable=sequences_var, values=["Default Sequence", "Custom Enter Sequence"])
sequence_dropdown.pack()

# Add Click button to generate new "Drag Me" buttons
add_click_button = tk.Button(root, text="Add Click", command=add_click_button)
add_click_button.pack(pady=10)

# Start and Stop buttons
start_button = tk.Button(root, text="Start", command=start_auto_clicker)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop", command=stop_auto_clicker)
stop_button.pack(pady=5)

# Predefined Sequences
predefined_sequences = {
    "Default Sequence": None,
    "Custom Enter Sequence": [
        {"type": "press", "key": "enter", "wait": 0.1},
        {"type": "hold", "key": "enter", "duration": 3.0, "wait": 0.2},
        {"type": "press", "key": "enter", "wait": 0.1}
    ]
}

# Global keyboard listeners for start and stop
keyboard.add_hotkey("enter", start_auto_clicker)  # Enter to start
keyboard.add_hotkey("esc", stop_auto_clicker)     # Esc to stop

# Run the main loop
root.mainloop()




