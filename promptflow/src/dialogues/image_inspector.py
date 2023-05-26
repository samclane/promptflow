"""
Display image in a dialogue box
"""

from PIL import ImageTk

import customtkinter


class ImageInspector(customtkinter.CTkToplevel):
    """
    Displays an image in a dialogue box
    """

    def __init__(self, master, image: ImageTk.PhotoImage):
        super().__init__(master)
        self.master = master
        self.image = image
        self.title("Image Inspector")
        self.canvas = customtkinter.CTkCanvas(
            self, width=self.image.width(), height=self.image.height()
        )
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.image, anchor="nw")
        self.canvas.update()
        self.grab_set()
        # bind scroll wheel to zoom
        self.canvas.bind("<MouseWheel>", self.handle_zoom)  # Windows
        self.canvas.bind("<Button-4>", self.handle_zoom)  # Linux (wheel up)
        self.canvas.bind("<Button-5>", self.handle_zoom)  # Linux (wheel down)
        self.canvas.bind("<4>", self.handle_zoom)  # MacOS (wheel up)
        self.canvas.bind("<5>", self.handle_zoom)  # MacOS (wheel down)

    def buttonbox(self):
        pass

    def destroy(self):
        super().destroy()
        self.image = None

    def handle_zoom(self, event):
        """
        Zooms in or out of the image
        """
        self.canvas.scale(
            "all",
            event.x,
            event.y,
            1 + event.delta / 1200,
            1 + event.delta / 1200,
        )
        self.canvas.update()
