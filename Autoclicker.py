import tkinter as tk
from tkinter import ttk
from submenu import SubMenu
import pyautogui
import threading
import time
import win32gui  # For handling window focusing
import keyboard  # Global keyboard listener (requires `pip install keyboard`)
import json  # To save and load sequences

# Initialize the Tkinter root window first
root = tk.Tk()
root.title("Auto Clicker")
root.geometry("500x400")

# Global variables to track buttons, click points, and minimized state
drag_buttons = []
click_positions = []
drag_windows = []
button_data = {}
sequences = []  # List to store sequences
sequence_file = 'sequences.json'  # File to store sequences

# To track the auto-clicker state
auto_clicker_running = threading.Event()

# Load sequences from the file (if any exist)
def load_sequences():
    try:
        with open(sequence_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Save the sequences to the JSON file
def save_sequences():
    try:
        with open(sequence_file, 'w') as f:
            json.dump(loaded_sequences, f, indent=4)
        print("Sequence saved successfully to JSON.")
    except Exception as e:
        print(f"Failed to save sequence to JSON: {e}")

# Function to list currently open windows
def get_open_windows():
    windows = []
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if window_title and len(window_title.strip()) > 0:
                windows.append(window_title)
    win32gui.EnumWindows(callback, None)
    return windows

# Create global Tkinter variables and UI elements
window_var = tk.StringVar(value="")
mode_var = tk.StringVar(value="Right Click")
sequences_var = tk.StringVar(value="Default Sequence")
loaded_sequences = load_sequences()  # Load existing sequences

# Dropdown to select the window to focus on
window_label = tk.Label(root, text="Select Window to Focus On:")
window_label.pack()
window_dropdown = ttk.Combobox(root, textvariable=window_var, values=get_open_windows())
window_dropdown.pack()

# Dropdown to select click mode
mode_label = tk.Label(root, text="Select Mode:")
mode_label.pack()
mode_dropdown = ttk.Combobox(root, textvariable=mode_var, values=["Right Click", "Left Click", "Enter Mode"])
mode_dropdown.pack()

# Dropdown for selecting a sequence
sequence_label = tk.Label(root, text="Select Sequence:")
sequence_label.pack()
sequence_dropdown = ttk.Combobox(root, textvariable=sequences_var, values=[seq['name'] for seq in loaded_sequences])
sequence_dropdown.pack()

# Function to add new "Drag Me" buttons
def add_click_button():
    button_name = f"Drag Me#{len(drag_windows) + 1}"
    create_floating_button(button_name)

    # If there are 2 or more buttons, show the Save button
    if len(drag_windows) >= 2:
        save_button.pack(pady=10)

# Add Click button
add_click_button_button = tk.Button(root, text="Add Click", command=add_click_button)
add_click_button_button.pack(pady=10)

# Function to create draggable buttons
def create_floating_button(button_name, button_info=None, position=None):
    button_window = tk.Toplevel()
    button_window.overrideredirect(True)

    # If position is provided, set it; otherwise, use default placement
    if position:
        button_window.geometry(f"+{position[0]}+{position[1]}")
    else:
        # Set the window to a default position (somewhere on the screen, not 0,0)
        button_window.geometry("100x50+200+200")  # You can customize the default position here

    button_window.wm_attributes("-topmost", True)

    drag_button = tk.Button(button_window, text=button_name, bg="lightblue")
    drag_button.pack(expand=True, fill='both')

    if button_info is None:
        default_mode = mode_var.get()
        # Initialize button data with default values
        button_data[button_name] = {
            "click_type": "Click",  # Default to "Click"
            "hold_duration": 1000,  # Default hold duration if "Hold" is selected
            "key_assignment": default_mode,  # Default to the selected mode
            "mouse_action": "None"  # None, Left Click, or Right Click
        }
    else:
        button_data[button_name] = button_info

    drag_windows.append(button_window)

    # Capture the button's actual position after it's been created
    button_window.update_idletasks()  # Force the window to update its position before capturing it
    x_position = button_window.winfo_x()
    y_position = button_window.winfo_y()

    # If the position is still (0, 0), explicitly set a default starting position
    if x_position == 0 and y_position == 0:
        x_position = 200  # Example starting position, can be customized
        y_position = 200  # Example starting position
        button_window.geometry(f"+{x_position}+{y_position}")

    click_positions.append((x_position, y_position))

    def start_drag(event):
        button_window._drag_start_x = event.x
        button_window._drag_start_y = event.y

    def do_drag(event):
        x = event.x_root - button_window._drag_start_x
        y = event.y_root - button_window._drag_start_y
        button_window.geometry(f"+{x}+{y}")
        index = drag_windows.index(button_window)
        click_positions[index] = (x, y)

    # Create submenu and link it to update the button's data
    submenu = SubMenu(button_window, button_name, lambda: delete_button(button_window), button_data)

    # Bind right-click to open submenu
    drag_button.bind("<Button-3>", submenu.show_menu)
    drag_button.bind("<ButtonPress-1>", start_drag)
    drag_button.bind("<B1-Motion>", do_drag)

# Function to delete a button
def delete_button(button_instance):
    index = drag_windows.index(button_instance)
    drag_windows.pop(index)
    click_positions.pop(index)
    button_instance.destroy()

# Save the current sequence
# Save the current sequence to the JSON file
def save_sequence():
    sequence_name = "Sequence#" + str(len(loaded_sequences) + 1)
    sequence = {
        "name": sequence_name,
        "buttons": []
    }

    # Save each button's position and all properties (click type, hold duration, key assignment, etc.)
    for i, button_window in enumerate(drag_windows):
        button_name = f"Drag Me#{i + 1}"
        button_info = button_data.get(button_name, {})
        button_position = click_positions[i]
        sequence['buttons'].append({
            "name": button_name,
            "data": button_info,  # Save all properties from button_info (submenu settings)
            "position": button_position
        })

    # Store the button data specifically for this sequence
    sequence_button_data[sequence_name] = button_data.copy()  # Create a deep copy of button data for this sequence

    # Check if this sequence already exists and update it instead of appending a duplicate
    existing_sequence = next((seq for seq in loaded_sequences if seq['name'] == sequence_name), None)
    if existing_sequence:
        existing_sequence.update(sequence)
    else:
        loaded_sequences.append(sequence)

    sequences_var.set(sequence_name)
    save_sequences()  # Save to file

    # Update the sequence dropdown
    sequence_dropdown['values'] = [seq['name'] for seq in loaded_sequences]

# Apply submenu changes specific to the current sequence
def apply_submenu_changes(button_name, updated_data):
    # Ensure the changes are applied only to the current sequence's button data
    button_data[button_name].update(updated_data)
    sequence_button_data[sequences_var.get()] = button_data.copy()  # Update sequence-specific data

# Bind the sequence dropdown to load a sequence when selected
sequence_dropdown.bind("<<ComboboxSelected>>", lambda e: load_sequence())

# A dictionary to store button data for each sequence separately
sequence_button_data = {}

# Clear button_data when loading a new sequence to prevent sharing between sequences
def load_sequence():
    selected_sequence = sequences_var.get()
    for sequence in loaded_sequences:
        if sequence['name'] == selected_sequence:
            # Clear current buttons
            for button_window in drag_windows:
                button_window.destroy()
            drag_windows.clear()
            click_positions.clear()
            
            # Load the button data specific to this sequence
            button_data.clear()  # Ensure button_data is cleared for the new sequence
            button_data.update(sequence_button_data.get(selected_sequence, {}))  # Load sequence-specific data
            
            # Create the saved buttons with their properties
            for button in sequence['buttons']:
                create_floating_button(button['name'], button['data'], button['position'])

# Bind the sequence dropdown to load a sequence when selected
sequence_dropdown.bind("<<ComboboxSelected>>", lambda e: load_sequence())

# Save button (initially hidden)
save_button = tk.Button(root, text="Save Sequence", command=save_sequence)
save_button.pack_forget()


# Auto-clicker loop
def start_auto_clicker():
    def click_loop():
        while auto_clicker_running.is_set():
            for index, (x, y) in enumerate(click_positions):
                button_name = f"Drag Me#{index + 1}"  # Use the stored button name
                button_info = button_data.get(button_name, {})

                click_type = button_info.get("click_type", "Click")
                hold_duration = button_info.get("hold_duration", 1000)
                key_assignment = button_info.get("key_assignment", "Enter")
                mouse_action = button_info.get("mouse_action", "None")

                # Check for mouse action override
                if mouse_action == "Left Click":
                    pyautogui.leftClick(x, y)
                elif mouse_action == "Right Click":
                    pyautogui.rightClick(x, y)
                else:
                    if click_type == "Click":
                        pyautogui.press(key_assignment)
                    elif click_type == "Hold":
                        # Continuously send the keyDown signal while the key is "held"
                        end_time = time.time() + (hold_duration / 1000)
                        while time.time() < end_time:
                            pyautogui.keyDown(key_assignment)
                            time.sleep(0.05)  # Repeat every 50ms to simulate holding

                        pyautogui.keyUp(key_assignment)  # Release the key after hold

                time.sleep(0.2)  # Interval between actions

    # Minimize all "Drag Me" buttons when starting
    for button_window in drag_windows:
        button_window.withdraw()  # Hide the window
    
    auto_clicker_running.set()
    threading.Thread(target=click_loop).start()



# Function to stop the auto-clicker
def stop_auto_clicker():
    # Restore all "Drag Me" buttons when stopping
    for button_window in drag_windows:
        button_window.deiconify()  # Restore the window

    auto_clicker_running.clear()

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

# Global keyboard listeners
keyboard.add_hotkey("enter", start_auto_clicker)
keyboard.add_hotkey("esc", stop_auto_clicker)

# Start the Tkinter main loop
root.mainloop()






