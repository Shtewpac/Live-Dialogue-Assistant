# Combined source file created on 2023-11-03 16:04:44

# G:\Other computers\My Laptop\UMass_CS\CS326_WebProgramming\Live Dialogue Options\LIVE_DIALOGUE_OPTIONS\src\main_app.py
import tkinter as tk
import sys
import openai
import os

sys.path.append('G:/Other computers/My Laptop/UMass_CS/CS326_WebProgramming/Live Dialogue Options/LIVE_DIALOGUE_OPTIONS')

from config import OPENAI_API_KEY, SMART_LLM, FAST_LLM
from ui.ui_manager import UIManager
from summary.live_summary_manager import LiveSummaryManager
from dialogue_suggestions.gpt_assistance_manager import GPTAssistanceManager

openai.api_key = OPENAI_API_KEY
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\wkraf\\AppData\\Roaming\\gcloud\\application_default_credentials.json"


class LiveDialogueApp:
    def __init__(self, root):
        self.root = root
        self.gpt_assistance_manager = GPTAssistanceManager(SMART_LLM)
        self.live_summary_manager = LiveSummaryManager(FAST_LLM)
        self.ui_manager = UIManager(root, self.gpt_assistance_manager, self.live_summary_manager)
        
        # Now set the suggestion_text_widget for the GPTAssistanceManager
        self.gpt_assistance_manager.set_suggestion_text_widget(self.ui_manager.suggestion_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = LiveDialogueApp(root)
    root.mainloop()

# G:\Other computers\My Laptop\UMass_CS\CS326_WebProgramming\Live Dialogue Options\LIVE_DIALOGUE_OPTIONS\src\dialogue_suggestions\gpt_assistance_manager.py
# gpt_assistance_manager.py

import openai
import tkinter as tk

# Assistance levels:
# 0: No assistance
# 1: Moderate assistance
# 2: High assistance

class GPTAssistanceManager:
    def __init__(self, model, assistance_level=1):
        self.model = model
        self.assistance_level = assistance_level
        self.suggestion_text = None

    def set_suggestion_text_widget(self, suggestion_text_widget):
        self.suggestion_text = suggestion_text_widget

    def set_assistance_level(self, assistance_level):
        self.assistance_level = assistance_level

    def get_assistance(self, transcript, summary):
        # Generate OpenAI-based suggestions
        suggestions = self.generate_suggestions(transcript, summary)

        # Display the suggestions
        self.suggestion_text.delete(1.0, tk.END)  # Clear previous suggestions
        self.suggestion_text.insert(tk.END, suggestions)


    def generate_suggestions(self, transcript, summary):
        assistance_level = self.assistance_level

        # Determine the system message based on the assistance level
        system_message = ''
        if assistance_level == 0:
            return ''
        elif assistance_level == 1:
            system_message = 'You will be given the current summary of the conversation and the last 10 lines of dialogue. Your job is to help person A respond to person B. Give them a response that is relevant to the conversation and that will help them continue the conversation.'
        elif assistance_level == 2:
            system_message = 'You will be given the current summary of the conversation and the last 10 lines of dialogue. Your job is to help person A respond to person B. Provide a response in the style of person A that is relevant to the conversation and that will help them continue the conversation.'
        else:
            system_message = 'Invalid assistance level'

        # Add the conversation transcript and summary to the messages list
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Conversation Transcript:\n{transcript}\n\nConversation Summary:\n{summary}"}
        ]

        # Generate suggestions using the selected model (for chat models)
        response = openai.ChatCompletion.create(  # Updated this line to use ChatCompletion
            model=self.model,
            messages=messages,   # Use 'messages' parameter for chat models
            max_tokens=50  # Adjust the max tokens as needed
        )

        # Extract and return the suggestions
        suggestions = response.choices[0].message["content"].strip()
        return suggestions


# G:\Other computers\My Laptop\UMass_CS\CS326_WebProgramming\Live Dialogue Options\LIVE_DIALOGUE_OPTIONS\src\audio\audio_manager.py
import os
import threading
import time

import librosa
import soundfile as sf
import speech_recognition as sr
from google.cloud import speech
from pydub import AudioSegment
from pydub.playback import play


class AudioManager:
    def __init__(self, callback=None):
        self.is_recording = False
        self.recognizer = sr.Recognizer()
        self.callback = callback
        self.saved_audio_files = []
        self.audio_counter = 0
        self.default_sample_rate = 24000
        self.recorded_audio_path = os.path.abspath('LIVE_DIALOGUE_OPTIONS/data/recorded_audio')
        self.preprocessed_audio_path = os.path.abspath('LIVE_DIALOGUE_OPTIONS/data/preprocessed_audio')
        self.delete_existing_audio_files()

    
    def preprocess_audio(self, speech_file):
        # Load the audio file using librosa and resample it to the desired sample rate
        y_resampled, _ = librosa.load(speech_file, sr=self.default_sample_rate)
        
        # Convert the resampled audio back to a wav file
        converted_audio_path = os.path.join(self.preprocessed_audio_path, f"{os.path.splitext(os.path.basename(speech_file))[0]}_converted.wav")
        
        # Save the resampled audio using soundfile
        sf.write(converted_audio_path, y_resampled, self.default_sample_rate)
        
        return converted_audio_path


    def start_recording(self):
        print("\nStarting recording...")
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()

    def _record(self):
        while self.is_recording:
            self._record_snippet()
            self.audio_counter += 1
            time.sleep(0.2)

    def _record_snippet(self):
        with sr.Microphone() as source:
            print("Say something!")
            audio = self.recognizer.listen(source)
            audio_filename = self._save_audio(audio)
            self.saved_audio_files.append(audio_filename)

    def _save_audio(self, audio):
        audio_filename = f"audio_segment_{self.audio_counter}.wav"
        audio_path = os.path.join(self.recorded_audio_path, audio_filename)
        with open(audio_path, "wb") as file:
            file.write(audio.get_wav_data())
        return audio_path

    def stop_recording(self):
        print("\nStopping recording...")
        self.is_recording = False
        self.combine_and_transcribe()

    def combine_and_transcribe(self):
        combined_audio = self._combine_audio_files()
        audio_filename = f"combined_audio_{self.audio_counter}.wav"
        audio_path = os.path.join(self.recorded_audio_path, audio_filename)
        combined_audio.export(audio_path, format="wav")
        self.transcribe_with_diarization(audio_path)

    def _combine_audio_files(self):
        combined_audio = AudioSegment.empty()
        for audio_file in self.saved_audio_files:
            audio = AudioSegment.from_wav(audio_file)
            combined_audio += audio
        return combined_audio
    
    def construct_sentences(self, words_info):
        sentences = []
        sentence = []
        current_speaker = words_info[0].speaker_tag

        for word_info in words_info:
            # Check if there's a significant time gap or speaker change
            if sentence and (word_info.speaker_tag != current_speaker or 
                            word_info.start_time.seconds - sentence[-1]['end_time'].seconds > 1):
                sentences.append((current_speaker, ' '.join([w['word'] for w in sentence])))
                sentence = []
                current_speaker = word_info.speaker_tag

            sentence.append({
                'word': word_info.word,
                'start_time': word_info.start_time,
                'end_time': word_info.end_time,
                'speaker_tag': word_info.speaker_tag
            })

        # Add the last sentence
        if sentence:
            sentences.append((current_speaker, ' '.join([w['word'] for w in sentence])))

        return sentences
    
    def transcribe_with_diarization(self, speech_file):
        client = speech.SpeechClient()
        
        # Preprocess the audio file
        converted_audio_path = self.preprocess_audio(speech_file)

        with open(converted_audio_path, "rb") as audio_file:
        # with open(speech_file, "rb") as audio_file:
            content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)

        diarization_config = speech.SpeakerDiarizationConfig(
            enable_speaker_diarization=True,
            min_speaker_count=2,
            max_speaker_count=6,
        )
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.default_sample_rate,
            language_code="en-US",
            diarization_config=diarization_config,
        )
        try:
            print("Waiting for operation to complete...")
            response = client.recognize(config=config, audio=audio)
        except Exception as e:
            print(f"An error occurred: {e}")
            return

        result = response.results[-1]
        words_info = result.alternatives[0].words
        
        sentences = self.construct_sentences(words_info)
        print("Sentences: ", sentences)
        
        return sentences
        
    def delete_existing_audio_files(self):
        # Delete recorded audio files
        for file in os.listdir(self.recorded_audio_path):
            if file.endswith(".wav"):
                os.remove(os.path.join(self.recorded_audio_path, file))
        
        # # Delete preprocessed audio files
        # for file in os.listdir(self.preprocessed_audio_path):
        #     if file.endswith(".wav"):
        #         os.remove(os.path.join(self.preprocessed_audio_path, file))


def recording_test():
    # Setting up the Google Cloud credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\wkraf\\AppData\\Roaming\\gcloud\\application_default_credentials.json"

    # Create an AudioManager instance
    audio_manager = AudioManager()

    # Start recording
    audio_manager.start_recording()

    # For this example, I'm simulating a delay, which you can remove.
    time.sleep(10)  # Record for 10 seconds

    # Stop recording
    audio_manager.stop_recording()


def sample_audio_test():
    # Setting up the Google Cloud credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\wkraf\\AppData\\Roaming\\gcloud\\application_default_credentials.json"

    # Create an AudioManager instance
    audio_manager = AudioManager()

    # Path to your pre-recorded conversation wav file
    pre_recorded_file_path = os.path.abspath('LIVE_DIALOGUE_OPTIONS/samples/raw_audio_samples/DeepConvo.wav')

    # Call the transcription function on the pre-recorded file
    transcription = audio_manager.transcribe_with_diarization(pre_recorded_file_path)

    # Print the transcription
    print("Transcription:\n", transcription)


if __name__ == "__main__":
    # recording_test()
    sample_audio_test()


# G:\Other computers\My Laptop\UMass_CS\CS326_WebProgramming\Live Dialogue Options\LIVE_DIALOGUE_OPTIONS\src\ui\ui_manager.py
import tkinter as tk
from tkinter import scrolledtext, Entry, Button
from audio.audio_manager import AudioManager
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech


class UIManager:
    def __init__(self, root, gpt_assistance_manager, live_summary_manager):
        self.configure_root(root)
        self.initialize_variables()
        
        # Set the manager attributes before creating the UI elements
        self.audio_manager = AudioManager(self.update_transcript)
        self.gpt_assistance_manager = gpt_assistance_manager
        self.live_summary_manager = live_summary_manager
        
        # Now, you can safely create the UI elements
        self.create_UI_elements()

    def configure_root(self, root):
        self.root = root
        self.root.title("Live Dialogue Options")

    def initialize_variables(self):
        self.selected_model = tk.StringVar(value="gpt-3.5-turbo")

    def create_UI_elements(self):
        self.create_transcript_frame()
        self.create_input_entry()
        self.create_buttons()
        self.create_suggestion_frame()
        self.create_summary_frame()
        self.create_live_transcript_frame()
        # Here, after creating the suggestion_text, we set it in the GPTAssistanceManager.
        self.gpt_assistance_manager.suggestion_text = self.suggestion_text

    def create_transcript_frame(self):
        transcript_frame = self.create_frame(self.root)
        self.transcript_text = self.create_scrolled_text(transcript_frame)

    def create_input_entry(self):
        self.input_entry = Entry(self.root, width=40)
        self.input_entry.pack()

    def create_buttons(self):
        Button(self.root, text="Switch Assistance Level", command=self.switch_assistance_level).pack()
        
        # Button to get assistance using GPT
        Button(self.root, text="Get Assistance", command=self.call_gpt_assistance).pack()
        
        Button(self.root, text="Clear Transcript & Summary", command=self.clear_transcript_summary).pack()
        
        # Button to start recording using the audio_manager
        self.start_recording_button = Button(self.root, text="Start Recording", command=self.start_recording)
        self.start_recording_button.pack()
        
        # Button to stop recording using the audio_manager
        Button(self.root, text="Stop Recording", command=self.stop_recording).pack()

    # Added method to handle start recording button click
    def start_recording(self):
        # First, combine and transcribe previous audio snippets
        self.audio_manager.start_recording()
        self.start_recording_button.config(state=tk.DISABLED)

    # Added method to handle stop recording button click
    def stop_recording(self):
        self.audio_manager.stop_recording()
        self.start_recording_button.config(state=tk.NORMAL)

    def create_suggestion_frame(self):
        suggestion_frame = self.create_frame(self.root)
        self.add_label_to_frame(suggestion_frame, "GPT Suggestions:")
        self.suggestion_text = self.create_scrolled_text(suggestion_frame)

    def create_summary_frame(self):
        summary_frame = self.create_frame(self.root)
        self.add_label_to_frame(summary_frame, "Rolling Summary:")
        self.summary_text = self.create_scrolled_text(summary_frame)

    def create_live_transcript_frame(self):
        self.live_transcript_text = self.create_scrolled_text(self.root)

    def create_frame(self, root):
        frame = tk.Frame(root)
        frame.pack(padx=10, pady=10)
        return frame

    def add_label_to_frame(self, frame, text):
        tk.Label(frame, text=text).pack()

    def create_scrolled_text(self, parent):
        text_widget = scrolledtext.ScrolledText(parent, wrap=tk.WORD, width=50, height=5)
        text_widget.pack()
        return text_widget

    def switch_assistance_level(self):
        # Placeholder for switching assistance levels
        # You can implement different levels of assistance here
        pass

    def call_gpt_assistance(self):
        transcript = self.transcript_text.get(1.0, tk.END).strip()  # Get transcript from UI
        summary = self.summary_text.get(1.0, tk.END).strip()        # Get summary from UI
        self.gpt_assistance_manager.get_assistance(transcript, summary)


    def update_transcript(self, text):
        """Update the transcript text widget with the recognized text."""
        self.transcript_text.insert(tk.END, text + '\n')
        self.transcript_text.see(tk.END)  # auto-scroll to the end

        # Update the live summary every time new text is added to the transcript
        # Add a dash to start of the text
        text = "- " + text
        self.live_summary_manager.add_text_to_transcript(text)
        updated_summary = self.live_summary_manager.get_summary()
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, updated_summary)
        
        # Determine the last speaker
        last_speaker = self.live_summary_manager.identify_last_speaker()
        print("\nLast speaker:", last_speaker)
        if last_speaker == "B":
            self.call_gpt_assistance()

            
    def clear_transcript_summary(self):
        # Clear the transcript and summary text areas
        self.transcript_text.delete(1.0, tk.END)
        self.summary_text.delete(1.0, tk.END)



# G:\Other computers\My Laptop\UMass_CS\CS326_WebProgramming\Live Dialogue Options\LIVE_DIALOGUE_OPTIONS\src\summary\live_summary_manager.py
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
                {"role": "system", "content": "You are going to be given a transcribed conversation from two people. Your job is to summarize the conversation. Refer to the two people as person A and person B in the summary."},
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

