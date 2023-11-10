# Python file for audio_manager.py

class AudioManager:
    def __init__(self):
        # Initialize audio manager
        self.is_recording = False

    def start_recording(self):
        self.is_recording = True        
        return "Recording started."
    
    def is_recording(self):
        # Simulated check for audio recording
        return self.is_recording

    def stop_recording(self):
        self.is_recording = False
        return "Recording stopped."

    def get_transcript(self):
        # Simulated audio transcript
        return "This is a simulated transcript of the recorded audio."
