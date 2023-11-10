# Python file for gui_interface.py

from abc import ABC, abstractmethod

class GUIInterface(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def update_transcript(self, transcript):
        pass

    @abstractmethod
    def update_suggestions(self, suggestions):
        pass
