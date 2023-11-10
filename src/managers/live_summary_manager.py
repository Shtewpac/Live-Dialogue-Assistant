# Python file for live_summary_manager.py
from config import *
import openai
class LiveSummaryManager:
    def __init__(self, model):
        self.model = model
        self.live_transcript = []
        self.line_counter = 0
        self.rolling_summary = ""

    def add_text_to_transcript(self, text):
        """Append the recognized text to the transcript list and update the line counter."""
        self.live_transcript.append(text)
        self.line_counter += 1
        if self.line_counter >= 2:
            self.update_summary()
            self.line_counter = 0
    
    def set_live_transcript(self, text):
        """Set the live transcript to the provided text."""
        self.live_transcript = text
        self.line_counter = 0
        self.update_summary()


    def get_last_10_lines(self):
        """Fetch the last 10 lines of the transcript."""
        return "\n".join(self.live_transcript[-10:])

    def generate_summary_messages(self, last_10_lines):
        """Determine the messages to send to the model for summarization."""
        total_lines = len(self.live_transcript)

        if total_lines > 10:
            return [
                {"role": "system", "content": "You will be given the current summary of the conversation and the last 10 lines of dialogue. Your job is to update the current summary with any relevant information from the last 10 lines."},
                {"role": "user", "content": f"Summary:\n{self.rolling_summary}\n\nLast 10 Lines of Transcript:\n{last_10_lines}"}
            ]
        else:
            return [
                {"role": "system", "content": f"You are going to be given a transcribed conversation from two people. Your job is to summarize the conversation. Refer to the two people as {SPEAKER_A} and {SPEAKER_B} in the summary."},
                {"role": "user", "content": f"Transcript:\n{self.live_transcript}"}
            ]

    def update_summary(self):
        print("\nUpdating summary...")
        """Use the model to generate a summary based on the transcript."""
        last_10_lines = self.get_last_10_lines()
        messages = self.generate_summary_messages(last_10_lines)
        print("\nMessages:", messages, "\n")
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=2000  # Adjust the max tokens as needed
            )
            
            # Update the rolling summary
            self.rolling_summary = response.choices[0].message["content"].strip()
        
        except Exception as e:
            print("Error:", e)

    def get_summary(self):
        """Retrieve the current rolling summary."""
        return self.rolling_summary
    
    def generate_summary(self, transcript):
        self.set_live_transcript(transcript)
        print("\nLive Transcript:", self.live_transcript)
        return self.rolling_summary
    
    def identify_last_speaker(self):
        messages = [
            {"role": "system", "content": "You will be given the current summary of the conversation and the last 10 lines of dialogue. Your job is to determine whether 'person A' or 'person B' was the last to speak. If person A was the last to speak, type 'A'. If person B was the last to speak, type 'B'."},
            {"role": "user", "content": f"Summary:\n{self.rolling_summary}\n\nLast 10 Lines of Transcript:\n{self.get_last_10_lines()}"}
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return response.choices[0].message["content"].strip()

        except Exception as e:
            print("Error:", e)
            return None
