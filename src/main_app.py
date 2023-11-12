# Python file for main_app.py

# Import necessary modules
from config import *  # or other relevant configuration
from views.tkinter_gui import TkinterGUI
from views.pyqt_gui import PyQtGUI
from controllers.gpt_assistance_controller import GPTAssistanceController
from controllers.audio_controller import AudioController
from controllers.summary_controller import LiveSummaryController
from managers.gpt_assistance_manager import GPTAssistanceManager
from managers.audio_manager import AudioManager
from managers.live_summary_manager import LiveSummaryManager
# from application_state import ApplicationState  # if you're using application state

from multiprocessing import Queue
import openai
import os
import sys

from PyQt5.QtWidgets import QApplication  # Add this import for PyQt

openai.api_key = os.environ["OPENAI_KEY"]
# Print the openai key to make sure it's working
# print("OPENAI_KEY: " + openai.api_key)

def main():
    # Load configuration

    # Create command and result queues for AudioManager
    command_queue = Queue()
    result_queue = Queue()

    # Initialize Managers
    gpt_assistance_manager = GPTAssistanceManager(FAST_LLM)
    audio_manager = AudioManager(command_queue, result_queue)  # Pass queues as arguments
    live_summary_manager = LiveSummaryManager(FAST_LLM)

    # Initialize Controllers with Managers
    gpt_assistance_controller = GPTAssistanceController(gpt_assistance_manager)
    audio_controller = AudioController(audio_manager)
    summary_controller = LiveSummaryController(live_summary_manager)

    # Set up GUI
    app = QApplication(sys.argv)
    # gui = PyQtGUI(gpt_assistance_controller, audio_controller, summary_controller)
    gui = PyQtGUI(gpt_assistance_controller, audio_controller, summary_controller, command_queue, result_queue)

    # Start the GUI's main interaction loop
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

