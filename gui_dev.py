import os, requests, shutil, json, subprocess, sys, yaml, toml, platform, threading, time
from urllib import request

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

FONT = ("Yu Gothic UI", 12, "normal")

urls = {
    "updater": "https://github.com/yamato080915/mcserver-updater/archive/refs/heads/main.zip", 
    "purpur": "https://api.purpurmc.org/v2/purpur/"
}
jdkurls = {
    "Windows": [
        ["jdk21", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/21.0.6+7/openlogic-openjdk-21.0.6+7-windows-x64.zip", "openlogic-openjdk-21.0.6+7-windows-x64"], 
        ["jdk17", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/17.0.14+7/openlogic-openjdk-17.0.14+7-windows-x64.zip", "openlogic-openjdk-17.0.14+7-windows-x64"], 
        ["jdk11", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/11.0.26+4/openlogic-openjdk-11.0.26+4-windows-x64.zip", "openlogic-openjdk-11.0.26+4-windows-x64"],
        ["jdk8", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/8u442-b06/openlogic-openjdk-8u442-b06-windows-x64.zip", "openlogic-openjdk-8u442-b06-windows-x64"]
        ], 
    "Linux":[
        ["jdk21", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/21.0.6+7/openlogic-openjdk-21.0.6+7-linux-x64.tar.gz", "openlogic-openjdk-21.0.6+7-linux-x64"], 
        ["jdk17", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/17.0.14+7/openlogic-openjdk-17.0.14+7-linux-x64.tar.gz", "openlogic-openjdk-17.0.14+7-linux-x64"], 
        ["jdk11", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/11.0.26+4/openlogic-openjdk-11.0.26+4-linux-x64.tar.gz", "openlogic-openjdk-11.0.26+4-linux-x64"],
        ["jdk8", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/8u442-b06/openlogic-openjdk-8u442-b06-linux-x64.tar.gz", "openlogic-openjdk-8u442-b06-linux-x64"]
        ]
}
OS = platform.system()
pypath = f"py{"thon" if OS!="Windows" else ""}"

if not OS in list(jdkurls.keys()):
    sys.exit("Unsupported OS")

urls["jdk"] = jdkurls[OS]

class build:
    def __init__(self, folder="server"):
        self.proxy = False
        self.secret = ""
        self.setup(folder)
        self.install()
        shutil.rmtree("__cache__")
        os.mkdir("__cache__")
        self.versions = list(json.loads(requests.get(urls["purpur"]).text)["versions"])
        self.jdkpath = {"..\\jdk\\jdk11\\bin\\java": self.versions[:self.versions.index("1.16.5")+1], "..\\jdk\\jdk17\\bin\\java": self.versions[self.versions.index("1.16.5")+1:self.versions.index("1.19.2")+1], "..\\jdk\\jdk21\\bin\\java": self.versions[self.versions.index("1.19.3"):]}
        if os.path.isdir("proxy") and os.path.isfile("proxy/forwarding.secret"):
            self.proxy = True
            os.chdir("proxy")
    def setup(self, folder):
        if not os.path.isdir(folder):
            os.mkdir(folder)
        os.chdir(folder)
        self.cwd = os.getcwd()
        if not os.path.isdir("__cache__"):
            os.mkdir("__cache__")
        if not os.path.isdir("jdk"):
            os.mkdir("jdk")
    def install(self):#root.app.dlhook
        for i in urls["jdk"]:
            root.app.progress0["text"]=f"Downloading {i[0]}"
            if not os.path.isdir(f"jdk/{i[0]}"):
                root.app.dlstart = time.perf_counter_ns()
                root.app.speed = 0
                th = threading.Thread(target=lambda: request.urlretrieve(url=i[1], filename=f"__cache__/{i[0]}.{"zip" if OS=="Windows" else "tar.gz"}", reporthook=root.app.dlhook), name="download", daemon=True)
                th.start()
                th.join()
                shutil.unpack_archive(f"__cache__/{i[0]}.{"zip" if OS=="Windows" else "tar.gz"}", "jdk")
                shutil.move(f"./jdk/{i[2]}", f"./jdk/{i[0]}")
            root.app.pbar0["value"]+=1
        root.app.progress0["text"] = "updating mcserver-updater" if os.path.isfile("updater.py") else "installing mcserver-updater"
        with open("__cache__/updater.zip", "wb") as f:
            f.write(requests.get(urls["updater"]).content)
        shutil.unpack_archive("__cache__/updater.zip", "./__cache__")
        root.app.pbar["value"]+=100
        shutil.move("__cache__/mcserver-updater-main/main.py", "./updater.py")
        shutil.move("__cache__/mcserver-updater-main/README.md", "./README.md")
        root.app.pbar0["value"]+=1
    def insert(self, state, box, text):
        box.config(state="normal")
        box.insert('end', text)
        root.bottom["text"] = f"{state}{text.replace("\n", "")}"#[:30]}{"" if len(text)<=30 else "..."}"
        box.config(state="disabled")
    def build_proxy(self):
        root.app.proxylbl["text"] = "Building Velocity Server..."
        root.app.select(root.app.proxytab)
        if self.proxy:return
        if not os.path.isdir("proxy"):os.mkdir("proxy")
        self.jsonData = {"file": "./proxy/server.jar", "software": "velocity", "version": "", "build": 0, "jdk": "..\\jdk\\jdk21\\bin\\java".replace("\\","/" if OS!="Windows" else "\\"), "RAM": "512M"}
        with open("proxy.json", "w", encoding="utf-8") as f:
            json.dump(self.jsonData, f, indent=4)
        cmdData = "@echo off\npy updater.py proxy.json\nIF %ERRORLEVEL% == 0 (\n    cd proxy\n    ..\\jdk\\jdk21\\bin\\java -Xmx512M -Xms512M -jar server.jar nogui\n    pause\n) ELSE (\n    echo %ERRORLEVEL%\n    pause\n)"
        with open("./proxy.cmd", "w", encoding="utf-8") as f:
            f.write(cmdData)
        p = subprocess.Popen([pypath, "updater.py", "proxy.json"], stdout=subprocess.PIPE, text=True)
        for line in iter(p.stdout.readline, ''):
            try:
                line = line.strip()
                self.insert("Building velocity...", root.app.proxylog, line + '\n')
                root.app.proxylog.see(tk.END)
            except:
                break
        p.wait()
        os.chdir("proxy")
        p = subprocess.Popen(["..\\jdk\\jdk21\\bin\\java".replace("\\", "/" if OS!="Windows" else "\\"), "-Xmx512M", "-Xms512M", "-jar", "server.jar", "nogui"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=OS=="Windows", text=True)
        for line in iter(p.stdout.readline, ''):
            try:
                line = line.strip()
                self.insert("Building velocity...", root.app.proxylog, line + '\n')
                root.app.proxylog.see(tk.END)
                if "Done" in line:
                    break
            except:
                break
        p.communicate(input="end")
        self.proxy = True
        root.app.proxylbl["text"] = "Setting Velocity Server..."
        self.proxy_setting()
        self.forward()
        root.app.mcbuild()
        root.app.select(root.app.buildtab)
    def proxy_setting(self):
        velocity = toml.load(open("velocity.toml"))
        velocity["player-info-forwarding-mode"] = "modern"
        self.insert("Setting velocity...", root.app.proxylog, 'set player-info-forwarding-mode to modern\n')
        velocity["force-key-authentication"] = False
        self.insert("Setting velocity...", root.app.proxylog, 'set force-key-authentication to false\n')
        root.app.proxylog.see(tk.END)
        velocity["servers"] = {}
        velocity["forced-hosts"] = {}
        toml.dump(velocity, open('velocity.toml', mode='w'))
    def forward(self):
        with open("forwarding.secret", "r", encoding="utf-8") as f:
            self.secret = f.read()
    def build_mcserver(self, name="lobby", version="", ram="4G"):
        root.app.select(root.app.mctabs[name][0])
        os.chdir(self.cwd)
        if version=="":version = self.versions[-1]
        self.path = "..\\jdk\\jdk21\\bin\\java" if version in self.jdkpath["..\\jdk\\jdk21\\bin\\java"] else "..\\jdk\\jdk17\\bin\\java" if version in self.jdkpath["..\\jdk\\jdk17\\bin\\java"] else "..\\jdk\\jdk11\\bin\\java"
        if OS!="Windows":self.path = self.path.replace("\\", "/")
        self.jsonData = {"file": f"{name}/purpur.jar", "software": "purpur", "version": version, "build": 0, "version-up": False, "jdk": self.path, "RAM": ram}
        with open(f"{name}.json", "w", encoding="utf-8") as f:
            json.dump(self.jsonData, f, indent=4)
        cmdData = f"@echo off\npy updater.py {name}.json\nIF %ERRORLEVEL% == 0 (\n    cd {name}\n    {self.path} -Xmx{ram} -Xms{ram} -jar purpur.jar nogui\n    pause\n) ELSE (\n    echo %ERRORLEVEL%\n    pause\n)"
        with open(f"./{name}.cmd", "w", encoding="utf-8") as f:
            f.write(cmdData)
        if not os.path.isdir(name):os.mkdir(name)
        with open(f"{name}/eula.txt", "w", encoding="utf-8") as f:
            f.write("eula=true")
        p = subprocess.Popen([pypath, "updater.py", f"{name}.json"])
        for line in iter(p.stdout.readline, ''):
            try:
                line = line.strip()
                self.insert(f"Building {name} Server...", root.app.mctabs[name][2], line + '\n')
                root.app.proxylog.see(tk.END)
            except:
                break
        p.wait()
        os.chdir(name)
        p = subprocess.Popen([self.path, f"-Xmx{ram}", f"-Xms{ram}", "-jar", "purpur.jar", "nogui"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=OS=="Windows", text=True)
        for line in iter(p.stdout.readline, ''):
            try:
                line = line.strip()
                self.insert(f"Building {name} Server...", root.app.mctabs[name][2], line + '\n')
                root.app.mctabs[name][2].see(tk.END)
                if "Timings Reset" in line or 'For help, type "help"' in line:
                    break
            except:
                break
        p.communicate(input="stop")
        p.wait()
        self.velocity_setting(name)
    def velocity_setting(self, name="lobby"):
        if not self.proxy:return
        with open("server.properties", "r", encoding="utf-8") as f:
            properties = f.read().splitlines()
        text = ""
        for i, e in enumerate(properties):
            if "online-mode" in e:
                properties[i] = "online-mode=false"
                self.insert(f"Setting {name} Server for velocity...", root.app.mctabs[name][2], "set online-mode=false\n")
            text += f"\n{properties[i]}"
        with open("server.properties", "w", encoding="utf-8") as f:
            f.write(text)
        if os.path.isfile("paper.yml"):yml = "paper.yml"
        else:yml = "config/paper-global.yml"
        with open(yml, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        self.insert(f"Setting {name} Server for velocity...", root.app.mctabs[name][2], "set paper.yml\n")
        config["settings" if yml=="paper.yml" else "proxies"][f"velocity{"-support" if yml=="paper.yml" else ""}"]["enabled"] = True
        config["settings" if yml=="paper.yml" else "proxies"][f"velocity{"-support" if yml=="paper.yml" else ""}"]["online-mode"] = True
        config["settings" if yml=="paper.yml" else "proxies"][f"velocity{"-support" if yml=="paper.yml" else ""}"]["secret"] = self.secret
        with open(yml, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f)
        os.chdir("../proxy")
        velocity = toml.load(open("velocity.toml"))
        if [] == list(velocity["servers"].values()):
            velocity["servers"][name] = "127.0.0.1:25566"
            velocity["servers"]["try"] = [name]
        else:
            velocity["servers"][name] = f"127.0.0.1:{25565 + len(list(velocity["servers"].values()))}"
        toml.dump(velocity, open('velocity.toml', mode='w'))
        os.chdir(f"../{name}")
        text = ""
        for i, e in enumerate(properties):
            if "server-port" in e:
                properties[i] = f"server-port={25565 + 1 if len(list(velocity["servers"].values()))==2 else len(list(velocity["servers"].values()))}"
                self.insert(f"Setting {name} Server for velocity...", root.app.mctabs[name][2], f"set {name} port:{25565 + 1 if len(list(velocity["servers"].values()))==2 else len(list(velocity["servers"].values()))}\n")
            text += f"\n{properties[i]}"
        with open("server.properties", "w", encoding="utf-8") as f:
            f.write(text)
        
class main(ttk.Notebook):
    def __init__(self, master=None):
        super().__init__(master)
        self.s = ttk.Style()
        self.s.configure('TNotebook.Tab', font=FONT)
        self.sbtn = ttk.Style()
        self.sbtn.configure('my.TButton', font=FONT)
        self.buildtab = tk.Frame(self)
        self.buildtab.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)
        #BUILDTAB--------------------------------------------------------------
        self.setuplbl = ttk.Label(self.buildtab, text="Setting up...", font=FONT, anchor=tk.CENTER)
        self.setuplbl.grid(column=0, columnspan=2, row=0, sticky=tk.EW, padx=10, pady=10)
        self.buildtab.grid_columnconfigure(0, weight=1)
        #self.buildtab.grid_rowconfigure(1, weight=1)
        #PROGRESS FRAME--------------------------------------------------------
        self.pframe = tk.Frame(self.buildtab)
        self.pframe.grid(column=0, columnspan=2, row=1, sticky=tk.NSEW)
        self.progress0 = tk.Label(self.pframe, text="", font=FONT)
        self.pbar0 = ttk.Progressbar(self.pframe, maximum=5, mode="determinate")
        self.pbar = ttk.Progressbar(self.pframe, maximum=100, mode="determinate")
        self.progress = tk.Label(self.pframe, text="", font=FONT)
        self.progress0.grid(column=0, row=0, sticky=tk.EW, padx=10, pady=10)
        self.pbar0.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
        self.pbar.grid(column=0, row=2, sticky=tk.NSEW, padx=10, pady=10)
        self.progress.grid(column=0, row=3, sticky=tk.EW, padx=10, pady=10)
        self.pframe.grid_columnconfigure(0, weight=1)
        #PROXYTAB--------------------------------------------------------------
        self.proxytab = tk.Frame(self)
        self.proxytab.grid(row=0, column=0, sticky=tk.NSEW)
        self.proxylbl = tk.Label(self.proxytab, text="", font=FONT)
        self.proxylbl.grid(column=0, row=0, sticky=tk.EW)
        self.proxylog = scrolledtext.ScrolledText(self.proxytab, state="disabled", font=("Yu Gothic UI", 10, "normal"))
        self.proxylog.grid(column=0, row=1, sticky=tk.NSEW)
        self.proxytab.grid_columnconfigure(0, weight=1)
        self.proxytab.grid_rowconfigure(1, weight=1)
        #MAIN PROCESS----------------------------------------------------------
        self.add(self.buildtab, text="Build")
        self.add(self.proxytab, text="Proxy")
        self.mctabs = {}
        threading.Thread(target=self.setup, name="setup", daemon=True).start()
    def addtab(self):
        name = self.nameent.get()
        version = self.verbox.get()
        ram = self.rament.get()
        if name in self.mctabs:
            self.select(self.mctabs[name][0])
            return
        self.mctabs[name] = [tk.Frame(self)]
        self.mctabs[name][0].grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)
        self.add(self.mctabs[name][0], text=name)
        self.mctabs[name].append(tk.Label(self.mctabs[name][0], text="", font=FONT))
        self.mctabs[name][1].grid(column=0, row=0, sticky=tk.EW)
        self.mctabs[name].append(scrolledtext.ScrolledText(self.mctabs[name][0], state="disabled", font=("Yu Gothic UI", 10, "normal")))
        self.mctabs[name][2].grid(column=0, row=1, sticky=tk.NSEW)
        self.mctabs[name][0].grid_columnconfigure(0, weight=1)
        self.mctabs[name][0].grid_rowconfigure(1, weight=1)
        threading.Thread(target=lambda: self.builder.build_mcserver(name=name, version=version, ram=ram), name="build server", daemon=True).start()
    def dlhook(self, block_count, block_size, total_size):
        dltime = time.perf_counter_ns()-self.dlstart
        self.pbar.configure(maximum=total_size)
        dlspeed = round((block_size*10000000/(dltime*8192) + self.speed)/2, 1)
        if dlspeed == 0.0:dlspeed = 100.0
        time_ = int(((total_size-block_count*block_size))/(dlspeed*8192))
        #self.progress.set(int(block_count*block_size))
        self.pbar["value"] = int(block_count*block_size)
        if int(block_count*block_size/1024) > round(total_size/1024):self.progress.configure(text=f"Complete! {round(total_size/1024)}KB")
        elif (block_count*block_size/1024) != 0.0:self.progress.configure(text=f"{int(block_count*block_size/1024)}KB / {round(total_size/1024)}KB\n{dlspeed}Mbps 残り{time_}s")
        self.dlstart = time.perf_counter_ns()
        self.speed = round(block_size*10000000/(dltime*8192), 1)
    def setup(self):
        self.builder = build()
        self.pframe.grid_forget()
        self.pbar["value"] = 0
        self.pbar0["value"] = 0
        self.setuplbl.grid_forget()
        self.setuplbl["text"]="Build Velocity Server"
        self.setuplbl.grid(column=0, row=0, sticky=tk.EW, padx=10, pady=10)
        self.btn = ttk.Button(self.buildtab, text="Build", style='my.TButton', command=lambda: threading.Thread(target=self.builder.build_proxy, name="build proxy", daemon=True).start())
        self.btn.grid(column=1, row=0, padx=10, pady=10)
        if os.path.isdir(f"{root.folder}/proxy"):
            self.mcbuild()
    def mcbuild(self):
        self.sbox = ttk.Style()
        self.setuplbl["text"] = "Build Minecraft Server"
        self.btn.configure(command=self.addtab)
        self.namelbl = tk.Label(self.buildtab, text="Server Name", font=FONT)
        self.namelbl.grid(column=0, row=1, sticky=tk.EW, padx=10, pady=10)
        self.nameent = ttk.Entry(self.buildtab, justify=tk.CENTER, font=FONT, width=15)
        if not os.path.isdir(f"{root.folder}/lobby"):
            self.nameent.insert("end", "lobby")
        self.nameent.grid(column=1, row=1, padx=10, pady=10)
        self.nameent.focus_set()
        self.softlbl = tk.Label(self.buildtab, text="Software", font=FONT)
        self.softlbl.grid(column=0, row=2, sticky=tk.EW, padx=10, pady=10)
        self.softbox = ttk.Combobox(self.buildtab, values=["Purpur"], font=FONT, state="readonly", justify=tk.CENTER, width=10)
        self.softbox.set("Purpur")
        self.softbox.grid(column=1, row=2, padx=10, pady=10)
        self.verlbl = tk.Label(self.buildtab, text="Minecraft Version", font=FONT)
        self.verlbl.grid(column=0, row=3, sticky=tk.EW, padx=10, pady=10)
        self.verbox = ttk.Combobox(self.buildtab, values=sorted(self.builder.versions, reverse=True), font=FONT, state="readonly", justify=tk.CENTER, width=10, style="my.TCombobox")
        self.verbox.set(sorted(self.builder.versions, reverse=True)[0])
        self.verbox.grid(column=1, row=3, padx=10, pady=10)
        self.ramlbl = tk.Label(self.buildtab, text="Memory Allocation", font=FONT)
        self.ramlbl.grid(column=0, row=4, sticky=tk.EW, padx=10, pady=10)
        self.rament = ttk.Entry(self.buildtab, justify=tk.CENTER, font=FONT, width=15)
        self.rament.insert("end", "4G")
        self.rament.grid(column=1, row=4, padx=10, pady=10)

class window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minecraft Server Builder")
        self.geometry("600x360")
        self.dialog()
        #self.bind("<Control-o>", self.dialog)
        self.title_ = ttk.Label(self, text=self.folder, font=FONT)
        self.title_.grid(row=0, column=0)
        self.bottom = ttk.Label(self, text="", anchor=tk.E)#, font=FONT)
        self.bottom.grid(row=2, column=0, sticky=tk.EW)
        self.app = main(self)
        self.app.grid(row=1, column=0, sticky=tk.NSEW)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
    def dialog(self, event=None):
        self.folder = filedialog.askdirectory(initialdir="./", title="Select a server directory")
        if self.folder=="":
            sys.exit()

if __name__=="__main__":
    root = window()
    root.mainloop()