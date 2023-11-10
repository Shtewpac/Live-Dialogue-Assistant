# Python file for summary_controller.py

from managers.live_summary_manager import LiveSummaryManager
class LiveSummaryController:
    def __init__(self, live_summary_manager):
        self.live_summary_manager = live_summary_manager

    def generate_summary(self, transcript):
        return self.live_summary_manager.generate_summary(transcript)
