from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtGui import QFont, QColor

class CodeEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)

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
        # self.setEolVisibility(False) # Commented out due to potential issue

    def find_next_in_editor(self, search_text):
        if not search_text:
            return

        found = self.findFirst(
            search_text,
            False,  # Regular expression
            False,  # Case sensitive
            False,  # Whole word
            True,   # Wrap around
            True,   # Forward
            -1, -1  #-1,-1 for line and index to search from the beginning
        )
        if not found:
            # If not found from the beginning, try from the current position
            self.findFirst(
                search_text,
                False, False, False, True, True,
                *self.getCursorPosition()
            )

    def replace_in_editor(self, search_text, replace_text):
        if not search_text:
            return

        if self.hasSelectedText() and self.selectedText().lower() == search_text.lower():
            self.replace(replace_text)
        else:
            self.find_next_in_editor(search_text)

    def replace_all_in_editor(self, search_text, replace_text):
        if not search_text:
            return

        self.beginUndoAction()
        while self.findFirst(search_text, False, False, False, False, True, -1, -1):
            self.replace(replace_text)
        self.endUndoAction()