import tkinter as tk

class SubMenu:
    def __init__(self, master, button_name, remove_callback, button_data):
        self.window = tk.Toplevel(master)
        self.window.title(f"Settings for {button_name}")
        self.window.geometry("400x400")

        self.button_name = button_name
        self.button_data = button_data
        self.waiting_for_key = False  # Track when waiting for a key press

        # Store the remove_callback separately
        self.remove_callback = remove_callback

        # Click Type Selector
        self.click_type_var = tk.StringVar(value=self.button_data[button_name]["click_type"])
        tk.Label(self.window, text="Click Type:").pack()
        self.click_type_menu = tk.OptionMenu(self.window, self.click_type_var, "Click", "Hold")
        self.click_type_menu.pack()

        # Hold Duration Input
        tk.Label(self.window, text="Hold Duration (ms):").pack()
        self.hold_duration_entry = tk.Entry(self.window)
        self.hold_duration_entry.insert(0, str(self.button_data[button_name]["hold_duration"]))
        self.hold_duration_entry.pack()

        # Mouse Action Dropdown (None, Left Click, Right Click)
        self.mouse_action_var = tk.StringVar(value=self.button_data[button_name]["mouse_action"])
        tk.Label(self.window, text="Mouse Action:").pack()
        self.mouse_action_menu = tk.OptionMenu(self.window, self.mouse_action_var, "None", "Left Click", "Right Click")
        self.mouse_action_menu.pack()

        # Set Action Button (waits for key press)
        self.set_action_button = tk.Button(self.window, text="Set Action", command=self.wait_for_key)
        self.set_action_button.pack()

        # Apply Changes Button
        self.apply_button = tk.Button(self.window, text="Apply Changes", command=self.apply_changes)
        self.apply_button.pack()

        # Delete Button
        self.delete_button = tk.Button(self.window, text="Delete Button", command=self.remove_callback)
        self.delete_button.pack()

        self.window.withdraw()

    def wait_for_key(self):
        self.set_action_button.config(text="Waiting for input key...")
        self.window.bind("<Key>", self.capture_key)
        self.waiting_for_key = True

    def capture_key(self, event):
        if self.waiting_for_key:
            self.button_data[self.button_name]["key_assignment"] = event.keysym
            self.set_action_button.config(text=f"Key assigned: {event.keysym}")
            self.window.unbind("<Key>")
            self.waiting_for_key = False

    def apply_changes(self):
        # Apply the changes when the "Apply Changes" button is clicked
        self.button_data[self.button_name]["click_type"] = self.click_type_var.get()
        self.button_data[self.button_name]["hold_duration"] = int(self.hold_duration_entry.get())
        self.button_data[self.button_name]["mouse_action"] = self.mouse_action_var.get()
        print(f"Changes applied to {self.button_name}: {self.button_data[self.button_name]}")

    def show_menu(self, event=None):
        if not self.window.winfo_exists():
            self.__init__(self.window.master, self.button_name, self.remove_callback, self.button_data)
        self.window.deiconify()
        self.window.lift()



