# Project Structure

## Overview

This document provides an overview of the directory structure for the LIVE DIALOGUE OPTIONS project and describes the purpose of each directory.

## Directory Breakdown

- **data**: Contains audio data.
  - **preprocessed_audio**: Processed audio files ready for analysis and processing.
  - **raw_audio_samples**: Original raw audio samples.

- **transcripts**: Transcriptions of audio samples.

- **demos**: Demo scripts showcasing the functionality of the project.

- **documentation**: Documentation related to the project, including design docs and implementation details.
  - **project_implementation_steps.md**: Steps for project implementation.
  - **Project_Proposal.md**: Initial project proposal.

- **models**: Deep learning and machine learning models.
  - **pretrained**: Pretrained models ready for deployment.
  - **trained**: Custom trained models specific to the project.

- **outputs**: Contains outputs like logs and results.
  - **logs**: Log files for debugging and analysis.
  - **results**: Results from various processes and algorithms.

- **src**: Source code for the main application.
  - **dialogue_suggestions**: Modules related to dialogue suggestions.
  - **diarization**: Modules for speaker diarization.
  - **audio**: Audio processing modules.
  - **ui**: User interface components.

- **utils**: Utility scripts and modules that assist in various tasks.

- **tests**: Test scripts to ensure the functionality of the project.

- **assets**: Assets like images, icons, and other media files.

## File Descriptions

- **.gitignore**: Specifies intentionally untracked files to ignore.
- **live_dialogue_app.py**: Main application script.
- **requirements.txt**: Contains the list of dependencies for the project.
- **create_project_directory.py**: Script to create the project directory.


 ////////////////

 This Python code is for an application that uses OpenAI's GPT-3 model to assist with live dialogue, including making suggestions and summarizing conversation. It also features an audio manager to handle live recording and speech recognition via Google's Speech-to-Text API.

On a broad level:

- `main_app.py` is the entry point and main executing script that creates an instance of the application and starts it.
- `GPTAssistanceManager` class manages the interaction with GPT-3, asking it for assistance based on transcripts and summaries.
- `AudioManager` handles recording audio, combining audio files and transcribing them into text.
- `UIManager` handles creating and managing the user interface with Tkinter. UI Elements include dialogue transcript box, summary box, an input box for text entry, and various control buttons.
- `LiveSummaryManager` utilizes GPT-3 to create live summaries of ongoing dialogue.

On a specific level:

- In `main_app.py`, the environmental variables for the OpenAI API and Google Cloud are set. An instance of the root Tkinter window is created along with the GPTAssistanceManager, LiveSummaryManager, and UIManager.
- The `GPTAssistanceManager` in `gpt_assistance_manager.py` creates relevant system messages based on the requested assistance level, sends these messages along with the conversation transcript and summary to GPT-3, and handles the AI's responses.
- `AudioManager` in `audio_manager.py` records audio segments, combines them into a single audio file, and sends it to Google's Speech-to-Text API for transcription. The transcriptions are sent back to the application using a callback function.
- In `ui_manager.py`, UIManager creates the UI elements, binds functions to button clicks, (e.g., Get Assistance, Start Recording etc.), and handles functionality for updating the transcript and summary text fields.
- `LiveSummaryManager` in `live_summary_manager.py` takes the live transcript and updates the rolling summary by sending batches to the GPT-3 model for summarizing.
