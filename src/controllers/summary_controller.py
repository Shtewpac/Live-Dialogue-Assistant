# Python file for summary_controller.py

from managers.live_summary_manager import LiveSummaryManager
class LiveSummaryController:
    def __init__(self):
        self.live_summary_manager = LiveSummaryManager()

    def generate_summary(self, transcript):
        return self.live_summary_manager.generate_summary(transcript)
