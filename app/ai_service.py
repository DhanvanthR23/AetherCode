import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

load_dotenv()

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)

class AIService(QObject):
    generation_finished = pyqtSignal(str)
    guidance_finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.llm_api_key = os.getenv("LLM_API_KEY")
        if not self.llm_api_key:
            raise ValueError("LLM_API_KEY not found in .env file")

        genai.configure(api_key=self.llm_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.threadpool = QThreadPool()

    def _execute_task(self, target_func, on_result_slot, *args):
        worker = Worker(target_func, *args)
        worker.signals.result.connect(on_result_slot)
        worker.signals.error.connect(self.error.emit)
        self.threadpool.start(worker)

    def get_code_generation(self, user_prompt: str, code: str):
        self._execute_task(self._get_code_generation_sync, self.generation_finished.emit, user_prompt, code)

    def _get_code_generation_sync(self, user_prompt: str, code: str) -> str:
        # Example for Google Gemini:
        chat = self.model.start_chat(history=[])
        response = chat.send_message(
            f"You are a senior Python developer. Based on the user's request and their current code, provide the complete, functional Python code to accomplish the task. Only return the code, with no extra explanation. User request: {user_prompt}. Current code: {code}"
        )
        return response.text.strip()

    def get_socratic_guidance(self, user_prompt: str, code: str):
        self._execute_task(self._get_socratic_guidance_sync, self.guidance_finished.emit, user_prompt, code)

    def _get_socratic_guidance_sync(self, user_prompt: str, code: str) -> str:
        # Example for Google Gemini:
        chat = self.model.start_chat(history=[])
        response = chat.send_message(
            f"You are a friendly and encouraging Python programming mentor who uses the Socratic method. Do not write the code for the user. Instead, analyze their request and their current code, identify their mistake or the next logical step, and ask a single, guiding question to help them figure it out on their own. Keep your questions concise. User request: {user_prompt}. Current code: {code}"
        )
        return response.text.strip()
