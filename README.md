# AetherCode: Native AI Code Editor

## Project Overview

This project is a native desktop AI-powered code editor for Python, built using Python's `customtkinter` library for the graphical user interface. It provides AI-assisted coding through a connection to the Google Gemini API.

The application is designed with a clear separation of concerns, making it modular and extensible.

### Key Technologies:
*   **Language:** Python 3
*   **GUI:** `customtkinter`
*   **Syntax Highlighting:** `pygments`
*   **AI Integration:** `google-generativeai` (for Google Gemini)
*   **Environment Management:** `python-dotenv`

### Core Features:
*   **Full-fledged Code Editor:** A custom code editor widget with real-time Python syntax highlighting.
*   **File Explorer:** A file explorer to browse and open files.
*   **Resizable Panes:** UI elements can be resized using sashes.
*   **AI Assistant Modes:**
    *   **Generator Mode:** Directly generates Python code based on a user's prompt.
    *   **Mentor Mode:** Provides Socratic, question-based guidance to help the user solve problems themselves.
*   **Code Execution:** A "Run" button to execute the code written in the editor and display the `stdout` and `stderr` in an output console.
*   **Tabbed Interface:** Allows editing multiple files at once.
*   **File Explorer Context Menu:** Right-click context menus for creating, renaming, and deleting files and folders.
*   **Save and Save As:** Functionality to save files with keyboard shortcuts (Ctrl+S and Ctrl+Shift+S).

### Architecture:
*   **`main.py`:** The main entry point that initializes and runs the application.
*   **`app/app_window.py`:** Defines the main application window, orchestrates all UI components (editor, buttons, output panes), and handles user interactions.
*   **`app/code_editor.py`:** A custom `CTkFrame` widget that encapsulates the `CTkTextbox` and all logic for syntax highlighting using the `pygments` library.
*   **`app/ai_service.py`:** A dedicated service class that manages all interactions with the Google Gemini API, including prompt construction for the different AI modes.
*   **`app/sash.py`:** A custom widget to allow resizing of UI panes.
*   **`app/custom_tab.py`:** Defines a custom tab with a close button.
*   **`app/file_explorer_context_menu.py`:** Implements the right-click context menu for the file explorer.

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