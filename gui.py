import tkinter as tk

class app(tk.Frame):
    def __init__(self, master=None, bg="#ffffff"):
        super().__init__(master, background=bg)

root = tk.Tk()
root.geometry("600x360")

frame = app(master=root)
frame.pack(fill=tk.BOTH, expand=True)

root.mainloop()