import tkinter as tk, sys
from tkinter import ttk
from tkinter import filedialog

import terminal

folder = filedialog.askdirectory(initialdir="./", title="Select a server directory")

if len(folder)==0:
    sys.exit()

class main(ttk.Notebook):
    def __init__(self, master=None):
        super().__init__(master)
        buildtab = tk.Frame(self)
        buildtab.pack(fill=tk.BOTH, expand=True)
        self.add(buildtab, text="Build")
        self.terminal = terminal.terminal(buildtab)
        self.terminal.pack(fill=tk.BOTH, expand=True)

root = tk.Tk()
root.title("Minecraft Server Builder")
root.geometry("600x360")

title = ttk.Label(root, text=folder, font=("Yu Gothic UI", 12, "normal"))
title.pack()

app = main(root)
app.pack(fill=tk.BOTH, expand=True)

bottom = ttk.Label(root, text="",    anchor=tk.E)
bottom.pack(fill=tk.X)

root.mainloop()