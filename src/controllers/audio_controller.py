# Python file for audio_controller.py

from managers.audio_manager import AudioManager
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
    
