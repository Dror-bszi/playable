import tkinter as tk

class ButtonVisualizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PlayAble - Button Visualizer")
        self.root.geometry("300x120")

        self.label_var = tk.StringVar()
        self.label = tk.Label(self.root, textvariable=self.label_var, font=("Arial", 16))
        self.label.pack(expand=True, fill="both", pady=20)

        self.set_status("Waiting for gesture...")

    def set_status(self, message):
        self.label_var.set(message)

    def set_button(self, button):
        self.label_var.set(f"Pressed: {button.upper()}")

    def update(self):
        self.root.update_idletasks()
        self.root.update()

    def close(self):
        self.root.destroy()