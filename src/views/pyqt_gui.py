
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import pyqtSignal, QTimer
from multiprocessing import Queue, Process
from managers.audio_manager import create_audio_manager

# class PyQtGUI(QMainWindow):
#     transcript_update_signal = pyqtSignal(str)

#     def __init__(self, gpt_assistance_controller, audio_controller, summary_controller, command_queue, result_queue):
#         super().__init__()
#         self.title = "Live Dialogue Assistant"
#         self.gpt_assistance_controller = gpt_assistance_controller
#         self.audio_controller = audio_controller
#         self.summary_controller = summary_controller
#         self.transcript_update_signal.connect(self.update_frames)

#         # Initialize command and result queues for inter-process communication
#         self.command_queue = command_queue
#         self.result_queue = result_queue

#         # Start the audio manager process using the factory function
#         self.audio_manager_process = Process(target=self.audio_controller.audio_manager.run)
#         self.audio_manager_process.start()

#         # Initialize UI
#         self.initUI()

#         # Start a timer to periodically check for updates from the audio manager
#         self.update_timer = QTimer(self)
#         self.update_timer.timeout.connect(self.check_for_updates)
#         self.update_timer.start(1000)  # Check every second
    
#     def initUI(self):
#         self.setWindowTitle(self.title)
#         self.setGeometry(100, 100, 1600, 1200)  # Set position and size
        
#         # Set a default font for the text edit widgets
#         text_edit_font = QFont('Arial', 12)  # You can adjust the size as needed
        
#         # Set a larger font for labels
#         label_font = QFont('Arial', 16)  # Adjust the size as needed
        
#         layout = QVBoxLayout()
        
#         # Initialize recording state and timer for blinking effect
#         self.is_recording = False
#         self.blink_timer = QTimer(self)
#         self.blink_timer.timeout.connect(self.blink_recording_button)

#         # Create and configure the transcript label
#         transcript_label = QLabel("Conversation Transcript")
#         transcript_label.setFont(label_font)
#         layout.addWidget(transcript_label)

#         # Create and configure the transcript text edit widget
#         self.transcript_text = QTextEdit()
#         self.transcript_text.setFont(text_edit_font)
#         layout.addWidget(self.transcript_text)

#         # Create and configure the summary label
#         summary_label = QLabel("Conversation Summary")
#         summary_label.setFont(label_font)
#         layout.addWidget(summary_label)

#         # Create and configure the summary text edit widget
#         self.summary_text = QTextEdit()
#         self.summary_text.setFont(text_edit_font)
#         layout.addWidget(self.summary_text)

#         # Create and configure the suggestions label
#         suggestion_label = QLabel("Dialogue Suggestions")
#         suggestion_label.setFont(label_font)
#         layout.addWidget(suggestion_label)

#         # Create and configure the suggestions text edit widget
#         self.suggestion_text = QTextEdit()
#         self.suggestion_text.setFont(text_edit_font)
#         layout.addWidget(self.suggestion_text)

#         # Create and configure the start recording button
#         self.start_button = QPushButton("Start Recording", self)
#         self.start_button.setFont(label_font)  # Set the font for the button as well
#         self.start_button.clicked.connect(self.start_recording)
#         layout.addWidget(self.start_button)

#         # Create and configure the stop recording button
#         self.stop_button = QPushButton("Stop Recording", self)
#         self.stop_button.setFont(label_font)  # Set the font for the button as well
#         self.stop_button.clicked.connect(self.stop_recording)
#         layout.addWidget(self.stop_button)

#         # Set the central widget and layout
#         central_widget = QWidget()
#         central_widget.setLayout(layout)
#         self.setCentralWidget(central_widget)

#     def update_frames_callback(self, transcript):
#         # Call this method to emit the signal
#         self.transcript_update_signal.emit(transcript)

#     def display_error(self, error_message):
#         # Placeholder for displaying error messages
#         pass

#     def start_recording(self):
#         print("Start Recording Button Pressed")
#         self.command_queue.put('START')
#         self.is_recording = True
#         self.start_button.setText("Recording")
#         self.start_button.setEnabled(False)  # Disable the start button
#         self.blink_timer.start(500)  # Blink every 500 milliseconds

#     def stop_recording(self):
#         print("Stop Recording Button Pressed")
#         self.command_queue.put('STOP')
#         self.is_recording = False
#         self.start_button.setText("Start Recording")
#         self.start_button.setEnabled(True)  # Re-enable the start button
#         self.start_button.setStyleSheet("")  # Reset button style
#         self.blink_timer.stop()
        
#     def blink_recording_button(self):
#         if self.is_recording:
#             current_color = self.start_button.styleSheet()
#             new_color = "background-color: red;" if current_color == "" else ""
#             self.start_button.setStyleSheet(new_color)
#         else:
#             self.blink_timer.stop()  # Stop blinking when not recording


#     def check_for_updates(self):
#         # Check the result queue for updates from the audio manager
#         if not self.result_queue.empty():
#             update = self.result_queue.get()
#             # Process the update (e.g., update transcript)
#             # For example, if the update is a transcript:
#             self.transcript_update_signal.emit(update)

#     def update_transcript(self, transcript):
#         self.transcript_text.clear()
#         for line in transcript.split('\n'):
#             if "Person A" in line:
#                 color = QColor("blue")
#             elif "Person B" in line:
#                 color = QColor("red")
#             else:
#                 color = QColor("black")
#             self.transcript_text.setTextColor(color)
#             self.transcript_text.append(line)

#     def set_summary(self, summary):
#         self.summary_text.setPlainText(summary)

#     def set_suggestions(self, suggestions):
#         self.suggestion_text.setPlainText(suggestions)

#     def update_frames(self, transcript):
#         # Update the transcript, conversation summary, and suggestions

#         # Update the transcript
#         self.update_transcript(transcript)

#         # Update the conversation summary
#         summary = self.summary_controller.generate_summary(transcript)
#         print("Setting summary...")
#         self.set_summary(summary)

#         # Update the suggestions
#         suggestions = self.gpt_assistance_controller.handle_request_for_assistance(transcript, summary)
#         print("Setting suggestions...")
#         self.set_suggestions(suggestions)

class PyQtGUI(QMainWindow):
    transcript_update_signal = pyqtSignal(str)

    def __init__(self, gpt_assistance_controller, audio_controller, summary_controller, command_queue, result_queue):
        super().__init__()
        self.title = "Live Dialogue Assistant"
        self.gpt_assistance_controller = gpt_assistance_controller
        self.audio_controller = audio_controller
        self.summary_controller = summary_controller
        self.transcript_update_signal.connect(self.update_frames)

        # Initialize command and result queues for inter-process communication
        self.command_queue = command_queue
        self.result_queue = result_queue

        # Start the audio manager process using the factory function
        self.audio_manager_process = Process(target=self.audio_controller.audio_manager.run)
        self.audio_manager_process.start()

        # Initialize UI
        self.initUI()

        # Start a timer to periodically check for updates from the audio manager
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_for_updates)
        self.update_timer.start(1000)  # Check every second
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 1600, 1200)  # Set position and size
        
        # Set a default font for the text edit widgets
        text_edit_font = QFont('Arial', 12)  # You can adjust the size as needed
        
        # Set a larger font for labels
        label_font = QFont('Arial', 16)  # Adjust the size as needed
        
        layout = QVBoxLayout()
        
        # Initialize recording state and timer for blinking effect
        self.is_recording = False
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.blink_recording_button)

        # Create and configure the recording button
        self.record_button = QPushButton("Start Recording", self)
        self.record_button.setFont(QFont('Arial', 16))
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)


        # Create and configure the transcript label
        transcript_label = QLabel("Conversation Transcript")
        transcript_label.setFont(label_font)
        layout.addWidget(transcript_label)

        # Create and configure the transcript text edit widget
        self.transcript_text = QTextEdit()
        self.transcript_text.setFont(text_edit_font)
        layout.addWidget(self.transcript_text)

        # Create and configure the summary label
        summary_label = QLabel("Conversation Summary")
        summary_label.setFont(label_font)
        layout.addWidget(summary_label)

        # Create and configure the summary text edit widget
        self.summary_text = QTextEdit()
        self.summary_text.setFont(text_edit_font)
        layout.addWidget(self.summary_text)

        # Create and configure the suggestions label
        suggestion_label = QLabel("Dialogue Suggestions")
        suggestion_label.setFont(label_font)
        layout.addWidget(suggestion_label)

        # Create and configure the suggestions text edit widget
        self.suggestion_text = QTextEdit()
        self.suggestion_text.setFont(text_edit_font)
        layout.addWidget(self.suggestion_text)

        # # Create and configure the start recording button
        # self.start_button = QPushButton("Start Recording", self)
        # self.start_button.setFont(label_font)  # Set the font for the button as well
        # # self.start_button.clicked.connect(self.start_recording)
        # layout.addWidget(self.start_button)

        # # Create and configure the stop recording button
        # self.stop_button = QPushButton("Stop Recording", self)
        # self.stop_button.setFont(label_font)  # Set the font for the button as well
        # # self.stop_button.clicked.connect(self.stop_recording)
        # layout.addWidget(self.stop_button)

        # Set the central widget and layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def update_frames_callback(self, transcript):
        # Call this method to emit the signal
        self.transcript_update_signal.emit(transcript)

    def display_error(self, error_message):
        # Placeholder for displaying error messages
        pass

    def toggle_recording(self):
        if self.is_recording:
            print("Stop Recording Button Pressed")
            self.command_queue.put('STOP')
            self.is_recording = False
            self.record_button.setText("Start Recording")
            self.record_button.setStyleSheet("")  # Reset button style
            self.blink_timer.stop()
        else:
            print("Start Recording Button Pressed")
            self.command_queue.put('START')
            self.is_recording = True
            self.record_button.setText("Stop Recording")
            self.blink_timer.start(500)  # Blink every 500 milliseconds

    def blink_recording_button(self):
        current_color = self.record_button.styleSheet()
        new_color = "background-color: red;" if current_color == "" else ""
        self.record_button.setStyleSheet(new_color)

    def check_for_updates(self):
        # Check the result queue for updates from the audio manager
        if not self.result_queue.empty():
            update = self.result_queue.get()
            # Process the update (e.g., update transcript)
            # For example, if the update is a transcript:
            self.transcript_update_signal.emit(update)

    def update_transcript(self, transcript):
        self.transcript_text.clear()
        for line in transcript.split('\n'):
            if "Person A" in line:
                color = QColor("blue")
            elif "Person B" in line:
                color = QColor("red")
            else:
                color = QColor("black")
            self.transcript_text.setTextColor(color)
            self.transcript_text.append(line)

    def set_summary(self, summary):
        self.summary_text.setPlainText(summary)

    def set_suggestions(self, suggestions):
        self.suggestion_text.setPlainText(suggestions)

    def update_frames(self, transcript):
        # Update the transcript, conversation summary, and suggestions

        # Update the transcript
        self.update_transcript(transcript)

        # Update the conversation summary
        summary = self.summary_controller.generate_summary(transcript)
        print("Setting summary...")
        self.set_summary(summary)

        # Update the suggestions
        suggestions = self.gpt_assistance_controller.handle_request_for_assistance(transcript, summary)
        print("Setting suggestions...")
        self.set_suggestions(suggestions)



# # Sample test code to run the application
# if __name__ == '__main__':
#     import sys
#     app = QApplication(sys.argv)
#     ex = PyQtGUI()
#     ex.show()
#     sys.exit(app.exec_())
