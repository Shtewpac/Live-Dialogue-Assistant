# Python file for gui_interface.py

from abc import ABC, abstractmethod

class GUIInterface(ABC):

    @abstractmethod
    def initialize(self, *args, **kwargs):
        """Initialize the GUI with necessary parameters."""
        pass

    @abstractmethod
    def start(self):
        """Start and display the GUI."""
        pass

    @abstractmethod
    def stop(self):
        """Close and stop the GUI."""
        pass

    @abstractmethod
    def update_transcript(self, transcript):
        """Update the transcript display."""
        pass

    @abstractmethod
    def update_suggestions(self, suggestions):
        """Update the suggestions display."""
        pass

    @abstractmethod
    def update_summary(self, summary):
        """Update the conversation summary display."""
        pass

    @abstractmethod
    def display_error(self, error_message):
        """Display an error message to the user."""
        pass
