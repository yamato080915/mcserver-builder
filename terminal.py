import tkinter as tk
import subprocess, platform

OS = platform.system()

class terminal(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.text = tk.Text(self)
        self.text.grid(column=0, row=0, sticky=tk.NSEW)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.text.config(state="disabled")
        self.scrollbar = tk.Scrollbar(self, command=self.text.yview)
        self.scrollbar.grid(column=1, row=0, sticky=tk.NS)
        self.text.config(yscrollcommand=self.scrollbar.set)
    def command(self, cmd):
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=OS=="Windows")
    def text_update(self):
        for line in iter(self.p.stdout.readline, ''):
            try:
                line = line.strip()
                self.text.config(state="normal")
                self.text.insert('end', line + '\n')
                self.text.config(state="disabled")
                if float(self.scrollbar.get()[1]) >= 0.9:self.text.see(tk.END)
            except:
                pass

if __name__=="__main__":
    root = tk.Tk()
    root.geometry("800x400")
    app = terminal(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()