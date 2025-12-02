# AetherCode: Native AI Code Editor

## Project Overview

This project is a native desktop AI-powered code editor for Python, built using Python's `PyQt6` library for the graphical user interface. It provides AI-assisted coding through a connection to the Google Gemini API and features a modern dark theme provided by the `pyqtdarktheme` library.

The application is designed with a clear separation of concerns, making it modular and extensible.

### Key Technologies:
*   **Language:** Python 3
*   **GUI:** `PyQt6`
*   **Code Editor:** `PyQt6-QScintilla`
*   **Theming:** `pyqtdarktheme`
*   **Syntax Highlighting:** `pygments`
*   **AI Integration:** `google-generativeai` (for Google Gemini)
*   **Environment Management:** `python-dotenv`

### Core Features:
*   **Full-fledged Code Editor:** A custom code editor widget with real-time Python syntax highlighting.
*   **File Explorer:** A file explorer to browse and open files.
*   **Resizable Panes:** UI elements can be resized.
*   **AI Assistant Modes:**
    *   **Generator Mode:** Directly generates Python code based on a user's prompt.
    *   **Mentor Mode:** Provides Socratic, question-based guidance to help the user solve problems themselves.
*   **Code Execution:** A "Run" button to execute the code written in the editor and display the `stdout` and `stderr` in an output console.
*   **Tabbed Interface:** Allows editing multiple files at once.
*   **File Management:** Open, Save, and Save As functionality with keyboard shortcuts.
*   **Project Management:** Open and manage entire folders as projects.

### Architecture:
*   **`main.py`:** The main entry point that initializes the QApplication and runs the PyQt6 application.
*   **`qt_ui/qt_app_window.py`:** Defines the main `QMainWindow`, orchestrates all UI components (editor, panels, menu), and handles user interactions using PyQt6.
*   **`qt_ui/qt_code_editor.py`:** Encapsulates the `QsciScintilla` widget and handles code editor features like syntax highlighting and line numbers.
*   **`app/ai_service.py`:** A dedicated service class that manages all interactions with the Google Gemini API, including prompt construction for the different AI modes.

---

## Building and Running

To get the application running, follow these steps.

### 1. Setup Virtual Environment
It is highly recommended to use a Python virtual environment to manage project dependencies.

```bash
# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies
Install all required libraries from the `requirements.txt` file.

```bash
# Ensure your virtual environment is activated
pip install -r requirements.txt
```

### 3. Configure API Key
The application requires a Google Gemini API key to function.

1.  Locate the `.env` file in the project root. If it doesn't exist, create one.
2.  Add your API key to it in the following format:
    ```
    LLM_API_KEY="your-google-gemini-api-key"
    ```



### 4. Run the Application

Once the dependencies are installed and the API key is configured, run the application from the project root directory:



```bash

python main.py

```




