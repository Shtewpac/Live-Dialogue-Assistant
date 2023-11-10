# Python file for gpt_assistance_controller.py

from managers.gpt_assistance_manager import GPTAssistanceManager

class GPTAssistanceController:
    def __init__(self):
        self.manager = GPTAssistanceManager(api_key="your-api-key")

    def handle_request_for_assistance(self, context):
        return self.manager.generate_suggestions(context)
