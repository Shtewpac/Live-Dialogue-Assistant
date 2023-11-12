# Python file for audio_manager.py

import os
from google.cloud import speech
import speech_recognition as sr
from pydub import AudioSegment
import threading
import time
import librosa
import soundfile as sf
import openai
from concurrent.futures import ThreadPoolExecutor

from config import *


def create_audio_manager(command_queue, result_queue):
    manager = AudioManager(command_queue, result_queue)
    manager.initialize()
    return manager
class AudioManager:
    def __init__(self, command_queue, result_queue):
        # Initialize audio manager
        self.command_queue = command_queue
        self.result_queue = result_queue
        self.transcript_update_callback = None
        self.is_recording = False
        self.recognizer = sr.Recognizer()
        self.saved_audio_files = []
        self.audio_counter = 0
        self.default_sample_rate = DEFAULT_SAMPLE_RATE
        self.recorded_audio_path = os.path.abspath('data/recorded_audio')
        self.preprocessed_audio_path = os.path.abspath('data/preprocessed_audio')
        self.combined_audio_path = os.path.join(self.recorded_audio_path, "combined_audio.wav")
        
        self.alternate_transcript = ""
        self.delete_existing_audio_files()

    def initialize(self):
        # Initialize threads, locks, or other non-picklable objects here
        self.new_snippet_event = threading.Event()

    def set_transcript_update_callback(self, callback):
        print("Transcript update callback triggered")
        self.transcript_update_callback = callback
    
    def run(self):
        print("Audio manager running...")
        self.initialize()
        while True:
            print("Running")
            command = self.command_queue.get()
            print("Command: ", command)

            if command == 'START':
                if not self.is_recording:
                    self.start_recording()
            elif command == 'STOP':
                if self.is_recording:
                    self.stop_recording()

            # Only call check_and_process_updates if recording is active
            if self.is_recording:
                self.check_and_process_updates()


    def check_and_process_updates(self):
        # This method will be called regularly to check if new audio snippets are available
        # and to process them. After processing, it will send updates back to the GUI.

        # Check if there are new audio snippets to process
        if self.new_snippet_event.is_set():
            # Combine audio files and transcribe
            self._combine_audio_files()
            transcript = self.get_transcript(self.combined_audio_path)

            # Send the transcript back to the GUI
            if transcript:
                self.result_queue.put(transcript)

            # Reset the event
            self.new_snippet_event.clear()

    def start_recording(self):
        print("Starting recording...")
        self.is_recording = True

        # Start recording loop in a new thread
        self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
        self.recording_thread.start()

        # Use threading for processing tasks instead of starting a new process
        self.processing_thread = threading.Thread(target=self._async_processing_loop, daemon=True)
        self.processing_thread.start()

    def stop_recording(self):
        self.is_recording = False

        # If using threads, ensure they are properly signaled to stop
        if hasattr(self, 'recording_thread') and self.recording_thread is not None:
            print("Waiting for recording thread to finish...")
            # Wait for the recording thread to finish, if necessary
            self.recording_thread.join()

        if hasattr(self, 'processing_thread') and self.processing_thread is not None:
            print("Waiting for processing thread to finish...")
            # Wait for the processing thread to finish, if necessary
            self.processing_thread.join()

        print("Recording stopped.")

    def is_recording(self):
        # Simulated check for audio recording
        return self.is_recording

    def _recording_loop(self):
        try:
            while self.is_recording:
                # print("Recording loop running")
                audio_data = self._record_snippet()
                if audio_data:
                    processed = self._process_snippet(audio_data)
                    if processed:
                        print("Snippet processed.")
                        self._store_snippet(audio_data)
                    else:
                        print("Snippet could not be processed.")
        except Exception as e:
            print(f"Exception in recording loop: {e}")

    def _async_processing_loop(self):
        while self.is_recording:
            time.sleep(1)  # Adjust the frequency of checks
            self.check_and_process_updates()

    def _store_snippet(self, audio_data):
        # Logic to store the audio snippet
        filename = f"snippet_{self.audio_counter}.wav"
        filepath = os.path.join(self.recorded_audio_path, filename)
        self.audio_counter += 1
        self.saved_audio_files.append(filepath)
        # Save the audio_data to file
        with open(filepath, "wb") as f:
            f.write(audio_data.get_wav_data())
        
        # After storing a new snippet:
        self.new_snippet_event.set()

    def _combining_and_transcribing_loop(self):
        while True:
            # print("Combining and transcribing loop running")

            # Wait for a new snippet or a stop signal
            self.new_snippet_event.wait()
            self.new_snippet_event.clear()
            if not self.is_recording and not self.saved_audio_files:
                break  # Exit the loop if recording is stopped and all files are processed

            if len(self.saved_audio_files) > 0:
                self._combine_audio_files()
                if self.combined_audio_path is not None:
                    transcript = self.get_transcript(self.combined_audio_path)
                    print("Transcript: ", transcript)
                    if transcript is not None:
                        self.transcript_update_callback(transcript)

    def _combine_audio_files(self):
        # print("Combining audio files...")
        combined_audio = AudioSegment.empty()
        # print("Saved audio files: ", self.saved_audio_files)
        for audio_file in self.saved_audio_files:
            audio = AudioSegment.from_file(audio_file)
            combined_audio += audio
        combined_audio.export(self.combined_audio_path, format="wav")

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
        try:
            transcription = self.recognizer.recognize_google(audio_data)
            print(f"\nRECOGNIZED: {transcription}")
            # Add the transcription to the alternate transcript
            self.alternate_transcript += transcription + "\n"
            return True
        except sr.UnknownValueError:
            print("Could not understand audio")
            return False
        except sr.RequestError as e:
            print(f"Request error from Google Speech Recognition service; {e}")
            return False


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
            try:
                sentences = self.transcribe_with_diarization(audio_file)
                if sentences is not None:
                    formatted_transcript = self.format_transcript(sentences)
                    # correct_transcript = self.correct_transcript(formatted_transcript)
                    print("\nAlternate transcript: ", self.alternate_transcript)
                    print("\nFormatted transcript: ", formatted_transcript)

                    correct_transcript = self.correct_transcript_compare(formatted_transcript, self.alternate_transcript)
                    # correct_transcript = formatted_transcript
                    return correct_transcript
            except Exception as e:
                print(f"An error occurred: {e}")
                return ""
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
    
    def correct_transcript_compare(self, transcript, alternate_transcript):
        # Reconstruct the transcript using gpt-3.5-turbo
        system_message = """
        You will be given two transcripts of the same conversation that may have discrepancies and errors. (Including which speaker is speaking, the number of times things are said, and the exact words used.)
        Your task is to compare these two transcripts and attempt to produce a single, accurate transcript that best represents what the actual conversation might have been. Consider differences in word choice, phrasing, and any potential errors in either transcript. 
        Provide the corrected and unified transcript. Give your answer in this form: 
        'Corrected Transcript:
        <Speaker X>: <text>
        <Speaker Y>: <text>
        ...'
        """
        # Construct the message for GPT
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Original Transcript:\n{transcript}\n"},
            {"role": "user", "content": f"Alternate Transcript:\n{alternate_transcript}\n"}
        ]

        # Generate suggestions using the selected model
        response = openai.ChatCompletion.create(
            # model=FAST_LLM,
            model=SMART_LLM,
            messages=messages,
            max_tokens=4000  # Adjust the max tokens as needed
        )

        # Extract and return the corrected transcript
        corrected_transcript = response.choices[0].message["content"].strip()
        # Remove the "Corrected Transcript: " prefix
        corrected_transcript = corrected_transcript.replace("Corrected Transcript:", "")
        # Remove the line break at the beginning of the transcript (if it exists)
        if corrected_transcript.startswith("\n"):
            corrected_transcript = corrected_transcript[1:]
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
            max_speaker_count=2,
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
        # print("Sentences: ", sentences)
        
        return sentences
    
    def delete_existing_audio_files(self):
        """Delete all existing audio files in the recorded and preprocessed audio directories."""
        for audio_dir in [self.recorded_audio_path, self.preprocessed_audio_path]:
            for filename in os.listdir(audio_dir):
                file_path = os.path.join(audio_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
    
