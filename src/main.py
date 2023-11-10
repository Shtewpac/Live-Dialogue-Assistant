from config import *
from views.tkinter_gui import TkinterGUI
from controllers.gpt_assistance_controller import GPTAssistanceController

def main():
    # Initialize the controller
    controller = GPTAssistanceController()

    # Initialize the GUI with the controller
    gui = TkinterGUI(controller)

    # Start the GUI
    gui.start()

if __name__ == "__main__":
    main()
