from tkinter import Canvas, Scrollbar, Frame, VERTICAL, LEFT, BOTH, Y, RIGHT, NW

def create_scrollable_frame(parent):
    """
    Creates a scrollable frame inside the given parent widget.
    Returns the inner frame where widgets can be placed.
    """
    canvas = Canvas(parent, bg="white", highlightthickness=0)
    scrollbar = Scrollbar(parent, orient=VERTICAL, command=canvas.yview)
    scrollable_frame = Frame(canvas, bg="white")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def _configure_canvas(event):
         if scrollable_frame.winfo_reqwidth() != canvas.winfo_width():
             canvas.itemconfigure(canvas_window, width=canvas.winfo_width())

    def _configure_frame(event):
        size = (scrollable_frame.winfo_reqwidth(), scrollable_frame.winfo_reqheight())
        canvas.config(scrollregion="0 0 %s %s" % size)
        if scrollable_frame.winfo_reqwidth() != canvas.winfo_width():
            canvas.config(width=scrollable_frame.winfo_reqwidth())


    scrollable_frame.bind('<Configure>', _configure_frame)
    canvas.bind('<Configure>', _configure_canvas)


    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    return scrollable_frame