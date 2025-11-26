# Gemini Project: Native AI Code Editor

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

### Architecture:
*   **`main.py`:** The main entry point that initializes and runs the application.
*   **`app/app_window.py`:** Defines the main application window, orchestrates all UI components (editor, buttons, output panes), and handles user interactions.
*   **`app/code_editor.py`:** A custom `CTkFrame` widget that encapsulates the `CTkTextbox` and all logic for syntax highlighting using the `pygments` library.
*   **`app/ai_service.py`:** A dedicated service class that manages all interactions with the Google Gemini API, including prompt construction for the different AI modes.
*   **`app/sash.py`:** A custom widget to allow resizing of UI panes.

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

1.  Locate the `.env` file in the project root.
2.  Add your API key to it in the following format:
    ```
    LLM_API_KEY="your-google-gemini-api-key"
    ```

### 4. Run the Application
Once the dependencies are installed and the API key is configured, run the application from the project root directory:

```bash
python main.py
```

---

## Development Roadmap

### To-Do List

- [x] Implement a native Menu Bar for discoverability and command organization.
- [x] Add a Tabbed Interface to allow editing multiple files at once.
- [x] Enhance File Explorer with right-click context menus (create, rename, delete).
- [x] Implement "Save" and "Save As" functionality with keyboard shortcuts.
- [x] Improve the overall UI theme to be more modern.
- [ ] Implement Project/Workspace Management to open and manage entire folders.
- [ ] Create a Global Find and Replace tool to search across all project files.
- [ ] Integrate a Terminal panel directly within the editor.

### Future Plans

#### Highly Recommended Features

-   **Real-time Linting & Error Highlighting:** Immediately flag errors and style issues in the code as the user types.
-   **Code Completion & IntelliSense:** Provide intelligent, context-aware suggestions for functions, variables, and modules.
-   **Command Palette:** A fast, searchable interface for accessing all editor commands.
-   **Git Integration:** Show the Git status of files (modified, new, untracked) in the UI and provide basic controls for staging and committing.
-   **Automatic Code Formatting:** Allow users to format their code with a single command.
-   **"Go to Definition":** The ability to instantly jump from a function call to its definition.

#### Advanced/Optional Features

-   **Integrated Debugger:** A complex but invaluable feature to set breakpoints, inspect variables, and step through code execution.
-   **Code Folding:** The ability to collapse/expand code blocks to reduce visual clutter.
-   **Multi-Cursor Editing:** A power-user feature for making simultaneous edits.
-   **Themes & Customization:** Allow users to change the editor's appearance (colors, fonts).
-   **AI-Powered Refactoring, Docstrings, & Tests:** More advanced AI features that can suggest improvements, generate documentation, and create unit tests.
-   **Extensibility & Plugin System:** The ultimate feature for long-term growth, allowing the community to build and share new functionality.

---

## Current Status

The application is in a stable state. All known issues have been resolved, and several new features have been implemented. The next step is to continue with the development roadmap.
