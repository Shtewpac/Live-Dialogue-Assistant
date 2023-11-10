# Python file for tkinter_gui.py

import tkinter as tk
from tkinter import messagebox, scrolledtext
from views.gui_interface import GUIInterface

class TkinterGUI(GUIInterface):
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Live Assistance Application")
        self.create_ui_elements()

    def initialize(self, *args, **kwargs):
        # Initialize any necessary parameters or configurations here
        pass

    def display_error(self, error_message):
        # Display an error message to the user in a popup messagebox
        messagebox.showerror("Error", error_message)

    def create_ui_elements(self):
        self.create_transcript_area()
        self.create_summary_area()
        self.create_suggestions_area()
        self.create_control_buttons()

    def create_transcript_area(self):
        self.transcript_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=10)
        self.transcript_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def create_summary_area(self):
        self.summary_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=5)
        self.summary_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def create_suggestions_area(self):
        self.suggestions_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=5)
        self.suggestions_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def create_control_buttons(self):
        tk.Button(self.root, text="Start", command=self.start_process).pack(side=tk.LEFT, padx=10)
        tk.Button(self.root, text="Stop", command=self.stop_process).pack(side=tk.LEFT, padx=10)

    def start_process(self):
        # Placeholder for start action
        pass

    def stop_process(self):
        # Placeholder for stop action
        pass

    def start(self):
        self.root.mainloop()

    def stop(self):
        self.root.destroy()

    def update_transcript(self, transcript):
        self.transcript_text.insert(tk.END, transcript + '\n')
        self.transcript_text.see(tk.END)
        
    def update_summary(self, summary):
        self.summary_text.insert(tk.END, summary + '\n')
        self.summary_text.see(tk.END)

    def update_suggestions(self, suggestions):
        self.suggestions_text.insert(tk.END, suggestions + '\n')
        self.suggestions_text.see(tk.END)
