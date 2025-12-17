from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import QTimer
import pycodestyle
import jedi

class CustomChecker(pycodestyle.Checker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = []

    def report_error(self, line_number, offset, msg, check):
        code = msg.split(" ")[0]
        self.errors.append((line_number, offset, msg, code))


class CodeEditor(QsciScintilla):
    INDICATOR_ERROR = 8
    INDICATOR_WARNING = 9

    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_search_text = ""
        self._last_search_options = {}

        # Set the font
        font = QFont()
        font.setFamily("monospace")
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)

        # Margin for line numbers
        fontmetrics = self.fontMetrics()
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.horizontalAdvance("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))

        # Brace matching
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

        # Indentation
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setBackspaceUnindents(True)
        self.setTabIndents(True)
        self.setAutoIndent(True)

        # Autocompletion
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAPIs)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionThreshold(1)
        self.completion_timer = QTimer(self)
        self.completion_timer.setInterval(500) # 500 ms delay
        self.completion_timer.setSingleShot(True)
        self.completion_timer.timeout.connect(self.show_completions)
        self.textChanged.connect(self.request_completions)

        # Caret
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#ffe4e4"))

        # Lexer for Python
        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)

        # EOL
        self.setEolMode(QsciScintilla.EolMode.EolUnix)

        # Linting
        self.indicatorDefine(QsciScintilla.IndicatorStyle.SquiggleIndicator, self.INDICATOR_ERROR)
        self.setIndicatorForegroundColor(QColor("red"), self.INDICATOR_ERROR)
        self.indicatorDefine(QsciScintilla.IndicatorStyle.SquiggleIndicator, self.INDICATOR_WARNING)
        self.setIndicatorForegroundColor(QColor("orange"), self.INDICATOR_WARNING)

        self.lint_timer = QTimer(self)
        self.lint_timer.setInterval(1000) # 1 second delay
        self.lint_timer.setSingleShot(True)
        self.lint_timer.timeout.connect(self.lint_code)
        self.textChanged.connect(self.request_lint)

    def request_lint(self):
        self.lint_timer.start()

    def lint_code(self):
        self.clear_all_indicators()
        
        lines = self.text().splitlines(True)
        
        # We need to use a custom checker to capture the errors
        # because pycodestyle.Checker prints them to stdout by default.
        checker = CustomChecker(filename=None, lines=lines)
        checker.check_all()

        for line_number, offset, msg, code in checker.errors:
            if code.startswith('E'):
                self.fillIndicatorRange(line_number - 1, offset, line_number - 1, self.lineLength(line_number - 1), self.INDICATOR_ERROR)
            elif code.startswith('W'):
                self.fillIndicatorRange(line_number - 1, offset, line_number - 1, self.lineLength(line_number - 1), self.INDICATOR_WARNING)

    def request_completions(self):
        self.completion_timer.start()

    def show_completions(self):
        line, index = self.getCursorPosition()
        text = self.text()

        # Assuming self.path is available. We need to set it when a file is opened.
        path = getattr(self, 'path', None)

        script = jedi.Script(code=text, path=path)
        completions = script.complete(line=line + 1, column=index)

        if completions:
            # Check if the autocompletion list is already active
            if not self.isListActive():
                # QScintilla's API for showing completions is a bit tricky.
                # We need to calculate the start of the word to be completed.
                word_start_pos = self.positionFromLineIndex(line, index) - len(completions[0].name_with_symbols) + len(completions[0].complete)
                
                completion_list = [c.name for c in completions]
                self.showUserList(1, completion_list)

    def clear_all_indicators(self):
        self.clearIndicatorRange(0, 0, self.lines() - 1, self.lineLength(self.lines() - 1), self.INDICATOR_ERROR)
        self.clearIndicatorRange(0, 0, self.lines() - 1, self.lineLength(self.lines() - 1), self.INDICATOR_WARNING)

    def find_first(self, search_text, options):
        if not search_text:
            return
        self._last_search_text = search_text
        self._last_search_options = options
        self.findFirst(
            search_text,
            options.get("regex", False),
            options.get("case_sensitive", False),
            options.get("whole_words", False),
            True  # wrap
        )

    def find_next_in_editor(self, search_text, options):
        if not search_text:
            return
        if self._last_search_text != search_text or self._last_search_options != options:
            self.find_first(search_text, options)
        else:
            self.findNext()

    def replace_in_editor(self, search_text, replace_text, options):
        if not search_text:
            return

        case_sensitive = options.get("case_sensitive", False)
        selected_text = self.selectedText()

        text_to_compare_selected = selected_text if case_sensitive else selected_text.lower()
        text_to_compare_search = search_text if case_sensitive else search_text.lower()

        if self.hasSelectedText() and text_to_compare_selected == text_to_compare_search:
            self.replace(replace_text)
            self.find_next_in_editor(search_text, options)
        else:
            self.find_next_in_editor(search_text, options)

    def replace_all_in_editor(self, search_text, replace_text, options):
        if not search_text:
            return

        self.beginUndoAction()
        self.setCursorPosition(0, 0)
        
        re = options.get("regex", False)
        cs = options.get("case_sensitive", False)
        wo = options.get("whole_words", False)

        while self.findFirst(search_text, re, cs, wo, False, True, *self.getCursorPosition()):
            self.replace(replace_text)

        self.endUndoAction()