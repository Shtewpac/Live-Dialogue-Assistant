# Python file for main_app.py

# Import necessary modules
from config import *  # or other relevant configuration
from views.tkinter_gui import TkinterGUI
from controllers.gpt_assistance_controller import GPTAssistanceController
from controllers.audio_controller import AudioController
from controllers.summary_controller import LiveSummaryController
from managers.gpt_assistance_manager import GPTAssistanceManager
from managers.audio_manager import AudioManager
from managers.live_summary_manager import LiveSummaryManager
# from application_state import ApplicationState  # if you're using application state

import openai
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS_PATH
openai.api_key = OPENAI_API_KEY

def main():
    # Load configuration

    # Initialize Managers
    gpt_assistance_manager = GPTAssistanceManager(FAST_LLM)
    audio_manager = AudioManager()  # Initialize with any required parameters
    live_summary_manager = LiveSummaryManager(FAST_LLM)

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

