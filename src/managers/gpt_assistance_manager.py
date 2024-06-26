# Python file for gpt_assistance_manager.py
import openai

class GPTAssistanceManager:
    def __init__(self, model, assistance_level=1):
        self.model = model
        self.assistance_level = assistance_level
        self.suggestion_text = None
        self.character = None

    def set_suggestion_text_widget(self, suggestion_text_widget):
        self.suggestion_text = suggestion_text_widget

    def set_assistance_level(self, assistance_level):
        self.assistance_level = assistance_level
        
    def set_character(self, character):
        self.character = character

    def generate_suggestions(self, transcript, summary):
        assistance_level = self.assistance_level

        # Determine the system message based on the assistance level
        system_message = ''
        if assistance_level == 0:
            return ''
        elif assistance_level == 1:
            system_message = 'You will be given the current summary of the conversation and the last lines of the transcript. Your job is to help person A respond to person B. Give them a response that is relevant to the conversation and that will help them continue the conversation. Your potential response should be no longer than a sentence or two. Give your answer in the following format: "Potential response:\n<response>"'
        elif assistance_level == 2:
            system_message = 'You will be given the current summary of the conversation and the last lines of the transcript. Your job is to help person A respond to person B. Provide a response in the style of person A that is relevant to the conversation and that will help them continue the conversation. Your potential response should be no longer than a sentence or two. Give your answer in the following format: "Potential response:\n<response>"'
        else:
            system_message = 'Invalid assistance level'
            
        if self.character is not None:
            system_message += f'\nRespond how {self.character} might respond.'
        

        # Add the conversation transcript and summary to the messages list
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Conversation Transcript:\n{transcript}\n\nConversation Summary:\n{summary}"}
        ]

        # Generate suggestions using the selected model (for chat models)
        response = openai.ChatCompletion.create(  # Updated this line to use ChatCompletion
            model=self.model,
            messages=messages,   # Use 'messages' parameter for chat models
            max_tokens=50  # Adjust the max tokens as needed
        )

        # Extract and return the suggestions
        suggestions = response.choices[0].message["content"].strip()
        # Remove the first line of the suggestions, which is the system message
        suggestions = suggestions.split('\n', 1)[1]
        return suggestions

