# Combined source file created on 2023-11-10 14:54:29

# Import necessary modules
from config import *  # or other relevant configuration

# Python file for gpt_assistance_controller.py
class GPTAssistanceController:
    def __init__(self, gpt_assistance_manager):
        self.manager = gpt_assistance_manager

    def handle_request_for_assistance(self, context):
        return self.manager.generate_suggestions(context)
    

# Python file for summary_controller.py
class LiveSummaryController:
    def __init__(self, live_summary_manager):
        self.live_summary_manager = live_summary_manager

    def generate_summary(self, transcript):
        return self.live_summary_manager.generate_summary(transcript)

# Python file for gpt_assistance_manager.py

class GPTAssistanceManager:
    def __init__(self, api_key):
        self.api_key = api_key

    def generate_suggestions(self, context):
        # In an actual scenario, you would make an API call to OpenAI here.
        # We're simulating with a static response for testing purposes.
        return f"Simulated response for context: {context}"

# Python file for audio_controller.py
class AudioController:
    def __init__(self, audio_manager):
        self.audio_manager = audio_manager

    def start_recording(self):
        return self.audio_manager.start_recording()
    
    def is_recording(self):
        return self.audio_manager.is_recording()

    def stop_recording(self):
        return self.audio_manager.stop_recording()

    def get_transcript(self):
        return self.audio_manager.get_transcript()
    
    def _combine_audio_files(self):
        return self.audio_manager._combine_audio_files()

# Python file for audio_manager.py

import os
from google.cloud import speech
import speech_recognition as sr
from pydub import AudioSegment
from queue import Queue
import threading
import time
import librosa
import soundfile as sf
import openai

class AudioManager:
    def __init__(self):
        # Initialize audio manager
        self.transcript_update_callback = None
        self.is_recording = False
        self.recognizer = sr.Recognizer()
        self.saved_audio_files = []
        self.audio_counter = 0
        self.default_sample_rate = DEFAULT_SAMPLE_RATE
        self.recorded_audio_path = os.path.abspath('data/recorded_audio')
        self.preprocessed_audio_path = os.path.abspath('data/preprocessed_audio')
        self.combined_audio_path = os.path.join(self.recorded_audio_path, "combined_audio.wav")
        self.recording_thread = None
        self.combining_thread = None
        self.delete_existing_audio_files()

    def set_transcript_update_callback(self, callback):
        self.transcript_update_callback = callback

    def start_recording(self):
        self.is_recording = True
        # Start recording loop
        # self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
        # self.recording_thread.start()
        threading.Thread(target=self._recording_loop, daemon=True).start()
        # Start processing loop
        self.combining_thread = threading.Thread(target=self._combining_and_transcribing_loop, daemon=True)
        self.combining_thread.start()
        print("Recording started.")
        # return "Recording started."
    
    def _recording_loop(self):
        while self.is_recording:
            audio_data = self._record_snippet()
            self._process_snippet(audio_data)
            # if audio data cannot be understood
            if self._process_snippet(audio_data):
                print("Snippet processed.")
                # Store snippet for later processing
                self._store_snippet(audio_data)
            else:
                print("Snippet could not be processed.")
            

    def _store_snippet(self, audio_data):
        # Logic to store the audio snippet
        filename = f"snippet_{self.audio_counter}.wav"
        filepath = os.path.join(self.recorded_audio_path, filename)
        self.audio_counter += 1
        self.saved_audio_files.append(filepath)
        # Save the audio_data to file
        with open(filepath, "wb") as f:
            f.write(audio_data.get_wav_data())

    def _combining_and_transcribing_loop(self):
        while self.is_recording or self.saved_audio_files:
            if len(self.saved_audio_files) > 1:
                self._combine_audio_files()
                # if combined_audio is not None:
                if self.combined_audio_path is not None:
                    transcript = self.get_transcript(self.combined_audio_path)
                    print("Transcript: ", transcript)
                    # Update the transcript in the UI
                    if transcript is not None:
                        self.transcript_update_callback(transcript)
            time.sleep(5)  # Wait some time before combining again

    def _combine_audio_files(self):
        combined_audio = AudioSegment.empty()
        print("Combining audio files...")
        print("Saved audio files: ", self.saved_audio_files)
        for audio_file in self.saved_audio_files:
            audio = AudioSegment.from_file(audio_file)
            combined_audio += audio
        combined_audio.export(self.combined_audio_path, format="wav")
    
    
    def is_recording(self):
        # Simulated check for audio recording
        return self.is_recording

    def stop_recording(self):
        self.is_recording = False
        # Join the recording thread
        self.recording_thread.join()
        # Join the combining thread
        self.combining_thread.join()
        print("Recording stopped.")

    def get_transcript(self):
        # Simulated audio transcript
        return "This is a simulated transcript of the recorded audio."
    
    def _record_snippet(self):
        # Logic to record a snippet of audio and return it
        # For example, using speech_recognition's listen() method
        with sr.Microphone() as source:
            print("Recording...")
            audio = self.recognizer.listen(source)
            return audio

    def _process_snippet(self, audio_data):
        # Transcribe the audio snippet
        try:
            transcription = self.recognizer.recognize_google(audio_data)
            print(f"Recognized: {transcription}")
            # if self.transcript_update_callback:
            #     self.transcript_update_callback(transcription)
            return transcription
        except sr.UnknownValueError:
            print("Could not understand audio")
            return False
        except sr.RequestError as e:
            print(f"Request error from Google Speech Recognition service; {e}")


    def format_transcript(self, transcript):
        # Format the transcript to include the speaker names
        formatted_transcript = ""
        current_speaker = None
        for sentence in transcript:
            speaker = sentence[0]
            text = sentence[1]
            if speaker != current_speaker:
                # formatted_transcript += "\n"
                pass
            if speaker == 1:
                formatted_transcript += f"{SPEAKER_A}: {text}\n"
            elif speaker == 2:
                formatted_transcript += f"{SPEAKER_B}: {text}\n"
            else:
                formatted_transcript += f"{text}\n"
            current_speaker = speaker
        return formatted_transcript
    
    def get_transcript(self, audio_file):
        if audio_file:
            sentences = self.transcribe_with_diarization(audio_file)
            if sentences is not None:
                formatted_transcript = self.format_transcript(sentences)
                correct_transcript = self.correct_transcript(formatted_transcript)
                return correct_transcript
        return ""
    
    def correct_transcript(self, transcript):
        # Reconstruct the transcript using gpt-3.5-turbo
        system_message = "You will be given a transcript of a conversation with potential errors. Please try and correct the transcript. Give your answer in this form: 'Corrected Transcript: <your corrected transcript>'"
        # Add the conversation transcript and summary to the messages list
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Conversation Transcript:\n{transcript}\n"}
        ]

        # Generate suggestions using the selected model (for chat models)
        response = openai.ChatCompletion.create(  # Updated this line to use ChatCompletion
            model="gpt-3.5-turbo-16k",
            messages=messages,   # Use 'messages' parameter for chat models
            max_tokens=4000  # Adjust the max tokens as needed
        )

        # Extract and return the suggestions
        corrected_transcript = response.choices[0].message["content"].strip()
        # Remove the "Corrected Transcript: " prefix
        corrected_transcript = corrected_transcript.replace("Corrected Transcript:", "")
        return corrected_transcript

    def preprocess_audio(self, speech_file):
        # Load the audio file using librosa and resample it to the desired sample rate
        y_resampled, _ = librosa.load(speech_file, sr=self.default_sample_rate)
        # Convert the resampled audio back to a wav file
        converted_audio_path = os.path.join(self.preprocessed_audio_path, f"{os.path.splitext(os.path.basename(speech_file))[0]}_converted.wav")
        # Save the resampled audio using soundfile
        sf.write(converted_audio_path, y_resampled, self.default_sample_rate)
        
        return converted_audio_path
    
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
        
        # Preprocess the audio file if necessary
        converted_audio_path = self.preprocess_audio(speech_file)

        with open(converted_audio_path, "rb") as audio_file:
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
            return None

        if not response.results:
            print("No results returned.")
            return None

        result = response.results[-1]
        words_info = result.alternatives[0].words if result.alternatives else []

        sentences = self.construct_sentences(words_info)
        print("Sentences: ", sentences)
        
        return sentences
    
    def delete_existing_audio_files(self):
        """Delete all existing audio files in the recorded and preprocessed audio directories."""
        for audio_dir in [self.recorded_audio_path, self.preprocessed_audio_path]:
            for filename in os.listdir(audio_dir):
                file_path = os.path.join(audio_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
    


# Python file for live_summary_manager.py

class LiveSummaryManager:
    def generate_summary(self, transcript):
        # Simulate the summarization of the transcript
        return f"Summary of the transcript: {transcript[:50]}..."


# Python file for gui_interface.py

from abc import ABC, abstractmethod

class GUIInterface(ABC):

    @abstractmethod
    def initialize(self, *args, **kwargs):
        """Initialize the GUI with necessary parameters."""
        pass

    @abstractmethod
    def start(self):
        """Start and display the GUI."""
        pass

    @abstractmethod
    def stop(self):
        """Close and stop the GUI."""
        pass

    @abstractmethod
    def update_transcript(self, transcript):
        """Update the transcript display."""
        pass

    @abstractmethod
    def update_suggestions(self, suggestions):
        """Update the suggestions display."""
        pass

    @abstractmethod
    def update_summary(self, summary):
        """Update the conversation summary display."""
        pass

    @abstractmethod
    def display_error(self, error_message):
        """Display an error message to the user."""
        pass

# Python file for tkinter_gui.py

import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

class TkinterGUI(GUIInterface):
    def __init__(self, gpt_assistance_controller, audio_controller, summary_controller, app_state=None):
        self.gpt_assistance_controller = gpt_assistance_controller
        self.audio_controller = audio_controller
        self.audio_controller.audio_manager.set_transcript_update_callback(self.set_transcript_callback)
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
        self.transcript_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=10)
        self.transcript_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def create_input_entry(self):
        self.input_entry = tk.Entry(self.root, width=40)
        self.input_entry.pack()

    def create_buttons(self):
        tk.Button(self.root, text="Switch Assistance Level", command=self.switch_assistance_level).pack()
        tk.Button(self.root, text="Get Assistance", command=self.get_assistance).pack()
        tk.Button(self.root, text="Clear Transcript & Summary", command=self.clear_transcript_summary).pack()
        tk.Button(self.root, text="Start Recording", command=self.start_recording).pack()
        tk.Button(self.root, text="Stop Recording", command=self.stop_recording).pack()

    def create_suggestion_frame(self):
        self.suggestion_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=5)
        self.suggestion_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def create_summary_frame(self):
        self.summary_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=5)
        self.summary_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

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

    def update_transcript(self, transcript):
        self.transcript_text.insert(tk.END, transcript + '\n')
        self.transcript_text.see(tk.END)

    def set_transcript(self, transcript):
        self.transcript_text.delete(1.0, tk.END)
        self.transcript_text.insert(tk.END, transcript + '\n')
        self.transcript_text.see(tk.END)

    def update_summary(self, summary):
        self.summary_text.insert(tk.END, summary + '\n')
        self.summary_text.see(tk.END)

    def update_suggestions(self, suggestions):
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

    def update_frames(self):
        # Update the transcript, conversation summary, and suggestions

        # Update the transcript
        transcript = self.audio_controller.get_transcript()
        self.update_transcript(transcript)

        # Update the conversation summary
        summary = self.summary_controller.generate_summary(transcript)
        self.update_summary(summary)

        # Update the suggestions
        suggestions = self.gpt_assistance_controller.generate_suggestions(transcript, summary)
        self.update_suggestions(suggestions)

# Python file for main_app.py

# from application_state import ApplicationState  # if you're using application state

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS_PATH
openai.api_key = OPENAI_API_KEY

def main():
    # Load configuration
    # Assuming API_KEY and other settings are loaded from config.py
    gpt_api_key = OPENAI_API_KEY

    # Initialize Managers
    gpt_assistance_manager = GPTAssistanceManager(gpt_api_key)
    audio_manager = AudioManager()  # Initialize with any required parameters
    live_summary_manager = LiveSummaryManager()

    # Initialize Controllers with Managers
    gpt_assistance_controller = GPTAssistanceController(gpt_assistance_manager)
    audio_controller = AudioController(audio_manager)
    summary_controller = LiveSummaryController(live_summary_manager)

    # (Optional) Set Dialogue State
    # application_state = ApplicationState()  # Initialize/Load state as needed

    # Set up GUI
    # gui = TkinterGUI(gpt_assistance_controller, audio_controller, summary_controller, application_state)
    gui = TkinterGUI(gpt_assistance_controller, audio_controller, summary_controller)

    # Start the GUI's main interaction loop
    gui.start()

if __name__ == "__main__":
    main()