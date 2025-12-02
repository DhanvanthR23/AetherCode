from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import QTimer
import pycodestyle

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
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionThreshold(1)

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
        checker = pycodestyle.Checker(filename='dummy.py', lines=lines)
        
        for line_number, offset, msg, _ in checker.check_all():
            code = msg.split(' ')[0]
            if code.startswith('E'):
                self.fillIndicatorRange(line_number - 1, offset, line_number - 1, self.lineLength(line_number - 1), self.INDICATOR_ERROR)
            elif code.startswith('W'):
                self.fillIndicatorRange(line_number - 1, offset, line_number - 1, self.lineLength(line_number - 1), self.INDICATOR_WARNING)

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

    def find_next(self, search_text, options):
        if not search_text:
            return
        if self._last_search_text != search_text or self._last_search_options != options:
            self.find_first(search_text, options)
        else:
            self.findNext()

    def replace_in_editor(self, search_text, replace_text, options):
        if not search_text:
            return

        if self.hasSelectedText() and self.selectedText() == search_text:
            self.replace(replace_text)
        else:
            self.find_first(search_text, options)

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
    
    def find_next_in_editor(self, search_text, options):
        self.find_next(search_text, options)
        if not search_text:
            return
        if self._last_search_text != search_text or self._last_search_options != options:
            self.find_first(search_text, options)
        else:
            self.findNext()

    def replace_in_editor(self, search_text, replace_text, options):
        if not search_text:
            return

        if self.hasSelectedText() and self.selectedText() == search_text:
            self.replace(replace_text)
        else:
            self.find_first(search_text, options)

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
    
    def find_next_in_editor(self, search_text, options):
        self.find_next(search_text, options)