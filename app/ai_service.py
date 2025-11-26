import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class AIService:
    def __init__(self):
        self.llm_api_key = os.getenv("LLM_API_KEY")
        if not self.llm_api_key:
            raise ValueError("LLM_API_KEY not found in .env file")

        # Initialize LLM client for Google Gemini:
        genai.configure(api_key=self.llm_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def get_code_generation(self, user_prompt: str, code: str) -> str:
        # Example for Google Gemini:
        chat = self.model.start_chat(history=[])
        response = chat.send_message(
            f"You are a senior Python developer. Based on the user's request and their current code, provide the complete, functional Python code to accomplish the task. Only return the code, with no extra explanation. User request: {user_prompt}. Current code: {code}"
        )
        return response.text.strip()

    def get_socratic_guidance(self, user_prompt: str, code: str) -> str:
        # Example for Google Gemini:
        chat = self.model.start_chat(history=[])
        response = chat.send_message(
            f"You are a friendly and encouraging Python programming mentor who uses the Socratic method. Do not write the code for the user. Instead, analyze their request and their current code, identify their mistake or the next logical step, and ask a single, guiding question to help them figure it out on their own. Keep your questions concise. User request: {user_prompt}. Current code: {code}"
        )
        return response.text.strip()

