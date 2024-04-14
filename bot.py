import requests
import uuid
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount
import google.generativeai as genai


class MyBot(ActivityHandler):
    def __init__(self):
        self.GOOGLE_API_KEY="AIzaSyAbTUC966hUyqc3e1eGrwdM2mgqkPOXafU"
        genai.configure(api_key=self.GOOGLE_API_KEY)
        self.user_language = "en"  # Initialize language preference
        self.subscription_key = "e5abe87017b24f27a6d03d16b4ff218f"  # Replace with your Azure Translator key
        self.endpoint = "https://api.cognitive.microsofttranslator.com"  # Azure Translator endpoint
        self.location = "eastus"  # Azure Translator region
        self.prevtext = "null"  # Initialize prevtext

    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text.lower()

        if ("language" in text) and (self.prevtext == "null"):
            # Prompt for language selection
            await turn_context.send_activity("Please choose a language for translation:")
            await turn_context.send_activity("1. English\n2. Marathi\n3. Hindi")
            self.prevtext = "language"
        elif ("1" in text) and (self.prevtext == "language"):
            self.user_language = "en"
            await turn_context.send_activity("You chose English.")
            await turn_context.send_activity("Let's continue in English.")
            self.prevtext = "null"
        elif ("2" in text) and (self.prevtext == "language"):
            self.user_language = "mr"
            await turn_context.send_activity("You chose Marathi.")
            await turn_context.send_activity("आपण मराठी निवडलं आहे। तरीही चालू ठेवा.")
            self.prevtext = "null"
        elif ("3" in text)  and (self.prevtext == "language"):
            self.user_language = "hi"
            await turn_context.send_activity("You chose Hindi.")
            await turn_context.send_activity("आप हिंदी चुनें जारी रखें.")
            self.prevtext = "null"
        else:
            # If the message is not related to language selection, proceed normally
            if text:
                # Translate text if user language is set
                if self.user_language:
                    translated_text = self.translate_text(text, self.user_language)
                    await turn_context.send_activity(f"Translation: {translated_text}")
                else:
                    await turn_context.send_activity("Please select a language first.")
                
                # Forward the user message to Gemini and get the response
                gemini_response = self.get_gemini_response(text)
                translated_gemini_response = self.translate_text(gemini_response, self.user_language)
                await turn_context.send_activity(translated_gemini_response)

    def translate_text(self, text, target_language):
        # Function to perform translation using Azure Translator API
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Ocp-Apim-Subscription-Region': self.location,  # Use the specified location
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())  # Add a unique client trace ID
        }

        body = [{'text': text}]
        params = {'api-version': '3.0', 'from': 'en', 'to': [target_language]}  # Update parameters for translation

        try:
            request_url = f'{self.endpoint}/translate'
            response = requests.post(request_url, headers=headers, params=params, json=body)
            response.raise_for_status()  # Raise an exception for non-200 status codes

            # Extract translated text from successful response
            translated_text = response.json()[0]['translations'][0]['text']
            return translated_text
        except Exception as e:
            print(f"An error occurred during translation: {e}")
            return "Translation failed."

    def get_gemini_response(self, text):
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(text)
        generated_text = response.text
        return generated_text

    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello Desi Dost bot Here!!!!")

# Create an instance of MyBot with your Gemini API key
BOT = MyBot()