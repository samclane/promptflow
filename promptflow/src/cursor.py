"""
Displays a cursor on the canvas.
"""
import tkinter as tk

from promptflow.src.themes import monokai


class FlowchartCursor:
    size_px = 10
    width = 2

    def __init__(
        self, canvas: tk.Canvas, center_x: float = 0, center_y: float = 0
    ) -> None:
        self.canvas = canvas
        self.center_x = center_x
        self.center_y = center_y
        self.draw()

    def draw(self):
        """
        Draw a plus sign on the canvas.
        """
        self.canvas.create_line(
            self.center_x - self.size_px / 2,
            self.center_y,
            self.center_x + self.size_px / 2,
            self.center_y,
            width=self.width,
            fill=monokai.COMMENTS,
            tags="cursor",
        )
        self.canvas.create_line(
            self.center_x,
            self.center_y - self.size_px / 2,
            self.center_x,
            self.center_y + self.size_px / 2,
            width=self.width,
            fill=monokai.COMMENTS,
            tags="cursor",
        )

    def move_to(self, new_x: float, new_y: float):
        """
        Clear the icon and draw a new cursor at the new location.
        """
        self.center_x = new_x
        self.center_y = new_y
        self.clear()
        self.draw()

    def clear(self):
        """
        Clear the cursor from the canvas.
        """
        self.canvas.delete("cursor")
