# Python file for gpt_assistance_controller.py

from managers.gpt_assistance_manager import GPTAssistanceManager

class GPTAssistanceController:
    def __init__(self, gpt_assistance_manager):
        self.manager = gpt_assistance_manager

    def handle_request_for_assistance(self, transcript, summary):
        return self.manager.generate_suggestions(transcript, summary)
