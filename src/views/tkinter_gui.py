# Python file for tkinter_gui.py

from views.gui_interface import GUIInterface

from config import *
import tkinter as tk
from tkinter import scrolledtext, messagebox

class TkinterGUI(GUIInterface):
    def __init__(self, gpt_assistance_controller, audio_controller, summary_controller, app_state=None):
        self.gpt_assistance_controller = gpt_assistance_controller
        self.audio_controller = audio_controller
        self.audio_controller.audio_manager.set_transcript_update_callback(self.update_frames_callback)
        self.summary_controller = summary_controller
        self.app_state = app_state  # Optional application state

        self.root = tk.Tk()
        self.root.title("Live Dialogue Assistant")
        self.create_ui_elements()

    def create_ui_elements(self):
        self.create_transcript_frame()
        self.create_input_entry()
        self.create_buttons()
        self.create_suggestion_frame()
        self.create_summary_frame()

    def create_transcript_frame(self):
        label = tk.Label(self.root, text="Conversation Transcript", font=("Arial", 14))
        label.pack(pady=(10, 0))
        self.transcript_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=10)
        self.transcript_text.pack(pady=(0, 10), padx=10, fill=tk.BOTH, expand=True)

        # Define tags for coloring
        self.transcript_text.tag_configure(SPEAKER_A, foreground="blue")
        self.transcript_text.tag_configure(SPEAKER_B, foreground="red")


    def create_input_entry(self):
        self.input_entry = tk.Entry(self.root, width=40)
        self.input_entry.pack()

    def create_buttons(self):
        tk.Button(self.root, text="Switch Assistance Level", command=self.switch_assistance_level).pack()
        tk.Button(self.root, text="Get Assistance", command=self.get_assistance).pack()
        tk.Button(self.root, text="Clear Transcript & Summary", command=self.clear_transcript_summary).pack()
        tk.Button(self.root, text="Start Recording", command=self.start_recording).pack()
        tk.Button(self.root, text="Stop Recording", command=self.stop_recording).pack()

    def create_summary_frame(self):
        label = tk.Label(self.root, text="Conversation Summary", font=("Arial", 14))
        label.pack(pady=(10, 0))
        self.summary_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=5)
        self.summary_text.pack(pady=(0, 10), padx=10, fill=tk.BOTH, expand=True)

    def create_suggestion_frame(self):
        label = tk.Label(self.root, text="Dialogue Suggestions", font=("Arial", 14))
        label.pack(pady=(10, 0))
        self.suggestion_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=5)
        self.suggestion_text.pack(pady=(0, 10), padx=10, fill=tk.BOTH, expand=True)

    
    # Implement the abstract methods
    def initialize(self, *args, **kwargs):
        pass

    def start(self):
        self.root.mainloop()

    def stop(self):
        self.root.destroy()

    def update_transcript_callback(self, transcript):
        # Ensure UI updates happen in the main thread
        self.root.after(0, lambda: self.update_transcript(transcript))

    def set_transcript_callback(self, transcript):
        # Ensure UI updates happen in the main thread
        self.root.after(0, lambda: self.set_transcript(transcript))

    def update_frames_callback(self, transcript):
        # Ensure UI updates happen in the main thread
        self.root.after(0, lambda: self.update_frames(transcript))

    def update_transcript(self, transcript):
        # Insert the new transcript
        self.transcript_text.insert(tk.END, transcript + '\n')
        self.transcript_text.see(tk.END)

    def set_transcript(self, transcript):
        self.transcript_text.delete(1.0, tk.END)
        lines = transcript.split('\n')
        for line in lines:
            line_end_index = tk.END
            self.transcript_text.insert(line_end_index, line + '\n')
            line_start_index = self.transcript_text.index(f"{line_end_index} -1 line linestart")
            line_end_index = self.transcript_text.index(f"{line_end_index} -1 line lineend")
            
            if "Person A" in line:
                self.transcript_text.tag_add("Person_A", line_start_index, line_end_index)
            elif "Person B" in line:
                self.transcript_text.tag_add("Person_B", line_start_index, line_end_index)
        self.transcript_text.see(tk.END)

    # def set_transcript(self, transcript):
    #     self.transcript_text.delete(1.0, tk.END)
    #     self.transcript_text.insert(tk.END, transcript + '\n')
    #     self.transcript_text.see(tk.END)

    def set_summary(self, summary):
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary + '\n')
        self.summary_text.see(tk.END)

    def set_suggestions(self, suggestions):
        self.suggestion_text.delete(1.0, tk.END)
        self.suggestion_text.insert(tk.END, suggestions + '\n')
        self.suggestion_text.see(tk.END)

    def display_error(self, error_message):
        messagebox.showerror("Error", error_message)

    # Placeholder methods for button commands
    def switch_assistance_level(self):
        pass

    def get_assistance(self):
        transcript = self.transcript_text.get(1.0, tk.END).strip()  # Get transcript from UI
        summary = self.summary_text.get(1.0, tk.END).strip()        # Get summary from UI
        if transcript:
            self.gpt_assistance_manager.get_assistance(transcript, summary)
        else:
            self.display_error("Please provide some input or start recording.")

    def clear_transcript_summary(self):
        self.transcript_text.delete(1.0, tk.END)
        self.summary_text.delete(1.0, tk.END)

    def start_recording(self):
        # Start recording audio
        self.audio_controller.start_recording()

    def stop_recording(self):
        # Signal the AudioManager to stop recording
        self.audio_controller.stop_recording()

    def update_frames(self, transcript):
        # Update the transcript, conversation summary, and suggestions

        # Update the transcript
        self.set_transcript(transcript)

        # Update the conversation summary
        summary = self.summary_controller.generate_summary(transcript)
        self.set_summary(summary)

        # Update the suggestions
        suggestions = self.gpt_assistance_controller.handle_request_for_assistance(transcript, summary)
        self.set_suggestions(suggestions)