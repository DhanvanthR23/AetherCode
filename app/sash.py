import customtkinter as ctk

class Sash(ctk.CTkFrame):
    def __init__(self, parent, col1, col2, is_vertical=True):
        super().__init__(parent, cursor="sb_h_double_arrow" if is_vertical else "sb_v_double_arrow")
        self.parent = parent
        self.col1 = col1
        self.col2 = col2
        self.is_vertical = is_vertical
        self.bind("<B1-Motion>", self._on_motion)

    def _on_motion(self, event):
        if self.is_vertical:
            # This is a simplified logic. A more robust implementation would consider
            # the total width and the proportions.
            w1 = self.parent.grid_columnconfigure(self.col1)['weight']
            w2 = self.parent.grid_columnconfigure(self.col2)['weight']
            
            # A simple adjustment based on mouse movement
            # This logic needs to be improved for a smooth resizing
            if event.x > 0:
                self.parent.grid_columnconfigure(self.col1, weight=w1 + 1)
                self.parent.grid_columnconfigure(self.col2, weight=max(1, w2 - 1))
            elif event.x < 0:
                self.parent.grid_columnconfigure(self.col1, weight=max(1, w1 - 1))
                self.parent.grid_columnconfigure(self.col2, weight=w2 + 1)
        else:
            w1 = self.parent.grid_rowconfigure(self.col1)['weight']
            w2 = self.parent.grid_rowconfigure(self.col2)['weight']
            if event.y > 0:
                self.parent.grid_rowconfigure(self.col1, weight=w1 + 1)
                self.parent.grid_rowconfigure(self.col2, weight=max(1, w2 - 1))
            elif event.y < 0:
                self.parent.grid_rowconfigure(self.col1, weight=max(1, w1 - 1))
                self.parent.grid_rowconfigure(self.col2, weight=w2 + 1)
