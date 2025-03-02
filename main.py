import os, requests, shutil, json, subprocess, sys, yaml, toml, platform, threading, time, glob
from urllib import request

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

arg = sys.argv

FONT = ("Yu Gothic UI", 12, "normal")

urls = {
    "updater": "https://github.com/yamato080915/mcserver-updater/archive/refs/heads/main.zip", 
    "purpur": "https://api.purpurmc.org/v2/purpur/", 
    "paper": "https://api.papermc.io/v2/projects/paper"
}
jdkurls = {
    "Windows": [
        ["jdk21", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/21.0.6+7/openlogic-openjdk-21.0.6+7-windows-x64.zip", "openlogic-openjdk-21.0.6+7-windows-x64"], 
        ["jdk17", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/17.0.14+7/openlogic-openjdk-17.0.14+7-windows-x64.zip", "openlogic-openjdk-17.0.14+7-windows-x64"], 
        ["jdk11", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/11.0.26+4/openlogic-openjdk-11.0.26+4-windows-x64.zip", "openlogic-openjdk-11.0.26+4-windows-x64"]#,
        #["jdk8", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/8u442-b06/openlogic-openjdk-8u442-b06-windows-x64.zip", "openlogic-openjdk-8u442-b06-windows-x64"]
        ], 
    "Linux":[
        ["jdk21", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/21.0.6+7/openlogic-openjdk-21.0.6+7-linux-x64.tar.gz", "openlogic-openjdk-21.0.6+7-linux-x64"], 
        ["jdk17", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/17.0.14+7/openlogic-openjdk-17.0.14+7-linux-x64.tar.gz", "openlogic-openjdk-17.0.14+7-linux-x64"], 
        ["jdk11", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/11.0.26+4/openlogic-openjdk-11.0.26+4-linux-x64.tar.gz", "openlogic-openjdk-11.0.26+4-linux-x64"]#,
        #["jdk8", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/8u442-b06/openlogic-openjdk-8u442-b06-linux-x64.tar.gz", "openlogic-openjdk-8u442-b06-linux-x64"]
        ]
}
OS = platform.system()
pypath = f'py{"thon3" if OS!="Windows" else ""}'

if not OS in list(jdkurls.keys()):
    sys.exit("Unsupported OS")

urls["jdk"] = jdkurls[OS]

def folderclear(folder):
    shutil.rmtree(folder)
    os.mkdir(folder)

class build:
    def __init__(self, app=None, folder="server"):
        self.folder = folder
        self.proxy = False
        self.secret = ""
        self.setup(folder)
        self.install(app)
        folderclear("__cache__")
        self.versions = {"purpur": list(json.loads(requests.get(urls["purpur"]).text)["versions"]), "paper": list(json.loads(requests.get(urls["paper"]).text)["versions"])}
        self.jdkpath = {
            "purpur": {"..\\jdk\\jdk11\\bin\\java": self.versions["purpur"][:self.versions["purpur"].index("1.16.5")+1], "..\\jdk\\jdk17\\bin\\java": self.versions["purpur"][self.versions["purpur"].index("1.16.5")+1:self.versions["purpur"].index("1.19.2")+1], "..\\jdk\\jdk21\\bin\\java": self.versions["purpur"][self.versions["purpur"].index("1.19.3"):]},
            "paper": {"..\\jdk\\jdk11\\bin\\java": self.versions["paper"][:self.versions["paper"].index("1.16.5")+1], "..\\jdk\\jdk17\\bin\\java": self.versions["paper"][self.versions["paper"].index("1.16.5")+1:self.versions["paper"].index("1.19.2")+1], "..\\jdk\\jdk21\\bin\\java": self.versions["paper"][self.versions["paper"].index("1.19.3"):]}
        }
        self.proxy = os.path.isdir("proxy") and os.path.isfile("proxy/forwarding.secret")
    def setup(self, folder):
        if not os.path.isdir(folder):
            os.mkdir(folder)
        os.chdir(folder)
        if not os.path.isdir("__cache__"):
            os.mkdir("__cache__")
        if not os.path.isdir("jdk"):
            os.mkdir("jdk")
    def install(self, app=None):
        for i in urls["jdk"]:
            app.progress0["text"]=f"Downloading {i[0]}"
            if not os.path.isdir(f"jdk/{i[0]}"):
                app.dlstart = time.perf_counter()
                th = threading.Thread(target=lambda: request.urlretrieve(url=i[1], filename=f'__cache__/{i[0]}.{"zip" if OS=="Windows" else "tar.gz"}', reporthook=app.dlhook), name="download", daemon=True)
                th.start()
                th.join()
                shutil.unpack_archive(f'__cache__/{i[0]}.{"zip" if OS=="Windows" else "tar.gz"}', "jdk")
                shutil.move(f"./jdk/{i[2]}", f"./jdk/{i[0]}")
            app.pbar0["value"]+=1
        app.progress0["text"] = "updating mcserver-updater" if os.path.isfile("updater.py") else "installing mcserver-updater"
        with open("__cache__/updater.zip", "wb") as f:
            f.write(requests.get(urls["updater"]).content)
        shutil.unpack_archive("__cache__/updater.zip", "./__cache__")
        root.app.pbar["value"]+=100
        shutil.move("__cache__/mcserver-updater-main/main.py", "./updater.py")
        shutil.move("__cache__/mcserver-updater-main/README.md", "./README.md")
        root.app.pbar0["value"]+=1
    def insert(self, state="", box=None, text=""):
        box.config(state="normal")
        box.insert('end', text)
        root.bottom["text"] = state + text.replace("\n", "")
        #[:30]}{"" if len(text)<=30 else "..."}"
        box.config(state="disabled")
    def build_proxy(self):
        root.app.proxytab.grid(row=0, column=0, sticky=tk.NSEW)
        root.app.add(root.app.proxytab, text="proxy")
        os.chdir(f"{self.folder}")
        root.app.btn["state"] = "disabled"
        root.app.proxylbl["text"] = "Building Velocity Server..."
        root.app.select(root.app.proxytab)
        if self.proxy:return
        if not os.path.isdir("proxy"):os.mkdir("proxy")
        self.jsonData = {"file": "./proxy/server.jar", "software": "velocity", "version": "", "build": 0, "jdk": "..\\jdk\\jdk21\\bin\\java".replace("\\","/" if OS!="Windows" else "\\"), "RAM": "512M"}
        with open("proxy.json", "w", encoding="utf-8") as f:
            json.dump(self.jsonData, f, indent=4)
        cmdData = "@echo off\npy updater.py proxy.json\nIF %ERRORLEVEL% == 0 (\n    cd proxy\n    ..\\jdk\\jdk21\\bin\\java -Xmx512M -Xms512M -jar server.jar nogui\n) ELSE (\n    echo %ERRORLEVEL%\n)"
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
                    p.stdin.write("end\n")
                    p.stdin.flush()
            except:
                break
        self.proxy = True
        root.app.proxylbl["text"] = "Setting Velocity Server..."
        self.proxy_setting()
        self.forward()
        root.app.mcbuild()
        root.app.select(root.app.buildtab)
        root.bottom["text"] = "Building Velocity Server...Complete!"
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
    def build_mcserver(self, name="lobby", software="purpur", version="", ram="4G"):
        root.app.select(root.app.mctabs[name]["frame"])
        os.chdir(self.folder)
        if version=="":version = self.versions[software][-1]
        self.path = "..\\jdk\\jdk21\\bin\\java" if version in self.jdkpath[software]["..\\jdk\\jdk21\\bin\\java"] else "..\\jdk\\jdk17\\bin\\java" if version in self.jdkpath[software]["..\\jdk\\jdk17\\bin\\java"] else "..\\jdk\\jdk11\\bin\\java"
        if OS!="Windows":self.path = self.path.replace("\\", "/")
        self.jsonData = {"file": f"{name}/{software}.jar", "software": software, "version": version, "build": 0, "version-up": False, "jdk": self.path, "RAM": ram}
        with open(f"{name}.json", "w", encoding="utf-8") as f:
            json.dump(self.jsonData, f, indent=4)
        cmdData = f"@echo off\npy updater.py {name}.json\nIF %ERRORLEVEL% == 0 (\n    cd {name}\n    {self.path} -Xmx{ram} -Xms{ram} -jar {software}.jar nogui\n) ELSE (\n    echo %ERRORLEVEL%\n)"
        with open(f"./{name}.cmd", "w", encoding="utf-8") as f:
            f.write(cmdData)
        if not os.path.isdir(name):os.mkdir(name)
        with open(f"{name}/eula.txt", "w", encoding="utf-8") as f:
            f.write("eula=true")
        p = subprocess.Popen([pypath, "updater.py", f"{name}.json"], stdout=subprocess.PIPE, text=True)
        for line in iter(p.stdout.readline, ''):
            try:
                line = line.strip()
                self.insert(f"Building {name} Server...", root.app.mctabs[name]["txt"], line + '\n')
                root.app.proxylog.see(tk.END)
            except:
                break
        p.wait()
        os.chdir(name)
        p = subprocess.Popen([self.path, f"-Xmx{ram}", f"-Xms{ram}", "-jar", f"{software}.jar", "nogui"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=OS=="Windows", text=True)
        for line in iter(p.stdout.readline, ''):
            try:
                line = line.strip()
                self.insert(f"Building {name} Server...", root.app.mctabs[name]["txt"], line + '\n')
                root.app.mctabs[name]["txt"].see(tk.END)
                if "Timings Reset" in line or 'For help, type "help"' in line:
                    p.stdin.write("stop\n")
                    p.stdin.flush()
            except:
                break
        p.wait()
        self.velocity_setting(name)
        root.app.btn["state"] = "enabled"
        root.app.proxyrun["state"] = "enabled"
        for i in list(root.app.mctabs.keys()):
            root.app.mctabs[i]["btnframe"]["run"]["state"] = "enabled"
        root.bottom["text"] = f"Building {name} Server...Complete!"
    def velocity_setting(self, name="lobby"):
        if not self.proxy:return
        with open("server.properties", "r", encoding="utf-8") as f:
            properties = f.read().splitlines()
        text = ""
        for i, e in enumerate(properties):
            if "online-mode" in e:
                properties[i] = "online-mode=false"
                self.insert(f"Setting {name} Server for velocity...", root.app.mctabs[name]["txt"], "set online-mode=false\n")
            text += f"\n{properties[i]}"
        with open("server.properties", "w", encoding="utf-8") as f:
            f.write(text)
        if os.path.isfile("paper.yml"):yml = "paper.yml"
        else:yml = "config/paper-global.yml"
        with open(yml, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        self.insert(f"Setting {name} Server for velocity...", root.app.mctabs[name]["txt"], "set paper.yml\n")
        config["settings" if yml=="paper.yml" else "proxies"][f'velocity{"-support" if yml=="paper.yml" else ""}']["enabled"] = True
        config["settings" if yml=="paper.yml" else "proxies"][f'velocity{"-support" if yml=="paper.yml" else ""}']["online-mode"] = True
        config["settings" if yml=="paper.yml" else "proxies"][f'velocity{"-support" if yml=="paper.yml" else ""}']["secret"] = self.secret
        with open(yml, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f)
        os.chdir("../proxy")
        velocity = toml.load(open("velocity.toml"))
        if [] == list(velocity["servers"].values()):
            velocity["servers"][name] = "127.0.0.1:25566"
            velocity["servers"]["try"] = [name]
        else:
            velocity["servers"][name] = f'127.0.0.1:{25565 + len(list(velocity["servers"].values()))}'
        toml.dump(velocity, open('velocity.toml', mode='w'))
        os.chdir(f"../{name}")
        text = ""
        for i, e in enumerate(properties):
            if "server-port" in e:
                properties[i] = 'server-port=' + str(25565 + (1 if len(list(velocity["servers"].values()))==2 else len(list(velocity["servers"].values()))-1))
                self.insert(f"Setting {name} Server for velocity...", root.app.mctabs[name]["txt"], f'set {name} port:' + str(25565 + (1 if len(list(velocity["servers"].values()))==2 else len(list(velocity["servers"].values()))-1)))
            text += f"\n{properties[i]}"
        with open("server.properties", "w", encoding="utf-8") as f:
            f.write(text)
        root.app.mctabs[name]["txt"].see(tk.END)
        
class main(ttk.Notebook):
    def __init__(self, master=None, folder="server"):
        super().__init__(master)
        self.running_p = {"proxy": None}
        self.folder = folder
        self.dlstart = 0
        self.s = ttk.Style()
        self.s.configure('TNotebook.Tab', font=FONT)
        self.sbtn = ttk.Style()
        self.sbtn.configure('my.TButton', font=FONT)
        if OS=="Windows":
            self.si = subprocess.STARTUPINFO()
            self.si.dwFlags = subprocess.STARTF_USESHOWWINDOW
            self.si.wShowWindow = subprocess.SW_HIDE
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
        self.pbar0 = ttk.Progressbar(self.pframe, maximum=4, mode="determinate")
        self.pbar = ttk.Progressbar(self.pframe, maximum=100, mode="determinate")
        self.progress = tk.Label(self.pframe, text="", font=FONT)
        self.progress0.grid(column=0, row=0, sticky=tk.EW, padx=10, pady=10)
        self.pbar0.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
        self.pbar.grid(column=0, row=2, sticky=tk.NSEW, padx=10, pady=10)
        self.progress.grid(column=0, row=3, sticky=tk.EW, padx=10, pady=10)
        self.pframe.grid_columnconfigure(0, weight=1)
        #PROXYTAB--------------------------------------------------------------
        self.proxytab = tk.Frame(self)
        self.proxylbl = tk.Label(self.proxytab, text="", font=FONT)
        self.proxylbl.grid(column=0, row=0, sticky=tk.EW)
        self.proxylog = scrolledtext.ScrolledText(self.proxytab, state="disabled", font=("Yu Gothic UI", 10, "normal"))
        self.proxylog.grid(column=0, row=1, sticky=tk.NSEW)
        self.shellframe = tk.Frame(self.proxytab)
        self.shellframe.grid(column=0, row=2, sticky=tk.EW)
        self.shelllbl = tk.Label(self.shellframe, text="Enterキーで送信", font=FONT)
        self.shelllbl.grid(column=0, row=0, sticky=tk.EW)
        self.shellent = tk.Entry(self.shellframe, font=FONT)
        self.shellent.grid(column=1, row=0, sticky=tk.EW)
        self.shellent.bind("<Return>", lambda event: self.shell("proxy"))#TODO
        self.shellframe.grid_columnconfigure(1, weight=1)
        #self.proxytab.grid_columnconfigure(0, weight=1)
        self.proxytab.grid_rowconfigure(1, weight=1)
        self.btnframe = tk.Frame(self.proxytab)
        self.btnframe.grid(column=0, row=3, sticky=tk.EW)
        self.proxyrun = ttk.Button(self.btnframe, text="Run", style='my.TButton', command=lambda: threading.Thread(target=lambda: self.server_runner("proxy"), name="run").start())
        self.proxyrun.grid(column=0, row=0)
        self.proxyend = ttk.Button(self.btnframe, text="Stop", style='my.TButton', command=lambda: self.stop("proxy"))
        self.proxyend.grid(column=1, row=0)
        self.proxyend = ttk.Button(self.btnframe, text="Kill", style='my.TButton', command=lambda: self.kill("proxy"))
        self.proxyend.grid(column=2, row=0)
        self.proxypanel = ttk.Frame(self.proxytab)
        self.proxypanel.grid(column=1, row=1, rowspan=3, sticky=tk.NSEW)
        #MAIN PROCESS----------------------------------------------------------
        self.add(self.buildtab, text="BUILD")
        self.mctabs = {}
        threading.Thread(target=self.setup, name="setup", daemon=True).start()
    def server_runner(self, server="proxy"):
        if server=="proxy":
            self.select(self.proxytab)
        else:
            self.select(self.mctabs[server]["frame"])
        os.chdir(self.folder)
        if OS=="Windows":
            self.running_p[server] = subprocess.Popen(f"{server}.cmd", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if server=="proxy":
                for line in iter(self.running_p[server].stdout.readline, ''):
                    try:
                        line = line.strip()
                        self.builder.insert(f"Running {server} Server...", self.proxylog, line + '\n')
                        self.proxylog.see(tk.END)
                    except:
                        break
            else:
                for line in iter(self.running_p[server].stdout.readline, ''):
                    try:
                        line = line.strip()
                        self.builder.insert(f"Running {server} Server...", self.mctabs[server]["txt"], line + '\n')
                        self.mctabs[server]["txt"].see(tk.END)
                    except:
                        break
        else:
            with open(f"./{server}.json", "r", encoding="utf-8") as f:
                jsondata = json.load(f)
            p = subprocess.Popen([pypath, "updater.py", f"./{server}.json"], stdout=subprocess.PIPE, text=True)
            p.wait()
            file = os.path.abspath(jsondata["file"])
            os.chdir(server)
            if server=="proxy":
                if not "jdk" in jsondata:jsondata["jdk"] = "..\\jdk\\jdk21\\bin\\java"
                if not "ram" in jsondata:jsondata["ram"] = "512M"
                self.running_p[server] = subprocess.Popen([jsondata["jdk"], f"-Xmx{jsondata["ram"]}", f"-Xms{jsondata["ram"]}", "-jar", file, "nogui"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
                for line in iter(self.running_p[server].stdout.readline, ''):
                    try:
                        line = line.strip()
                        self.builder.insert(f"Running {server} Server...", self.proxylog, line + '\n')
                        self.proxylog.see(tk.END)
                    except:
                        break
            else:
                version = jsondata["version"]
                software = jsondata["software"]
                if not "jdk" in jsondata:jsondata["jdk"] = "..\\jdk\\jdk21\\bin\\java" if version in self.builder.jdkpath[software]["..\\jdk\\jdk21\\bin\\java"] else "..\\jdk\\jdk17\\bin\\java" if version in self.builder.jdkpath[software]["..\\jdk\\jdk17\\bin\\java"] else "..\\jdk\\jdk11\\bin\\java"
                if not "ram" in jsondata:jsondata["ram"] = "4G"
                self.running_p[server] = subprocess.Popen([jsondata["jdk"], f"-Xmx{jsondata["ram"]}", f"-Xms{jsondata["ram"]}", "-jar", file, "nogui"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
                for line in iter(self.running_p[server].stdout.readline, ''):
                    try:
                        line = line.strip()
                        self.builder.insert(f"Running {server} Server...", self.mctabs[server]["txt"], line + '\n')
                        self.mctabs[server]["txt"].see(tk.END)
                    except:
                        break
    def stop(self, server="proxy"):
        if self.running_p[server]==None:
            if server=="proxy":self.builder.insert("", self.proxylog, "velocityはまだ開始されていません\n")
            else:self.builder.insert("", self.mctabs[server]["txt"], f"{server}はまだ開始されていません\n")
            return
        if self.running_p[server].poll()!=None:
            if server=="proxy":self.builder.insert("", self.proxylog, "velocityはすでに停止しています\n")
            else:self.builder.insert("", self.mctabs[server]["txt"], f"{server}はすでに停止しています\n")
            return
        if server=="proxy":
            self.running_p[server].stdin.write("end\n")
        else:
            self.running_p[server].stdin.write("stop\n")
        self.running_p[server].stdin.flush()
    def kill(self, server="proxy"):
        if self.running_p[server]==None:
            if server=="proxy":self.builder.insert("", self.proxylog, "velocityはまだ開始されていません\n")
            else:self.builder.insert("", self.mctabs[server]["txt"], f"{server}はまだ開始されていません\n")
            return
        if self.running_p[server].poll()!=None:
            if server=="proxy":self.builder.insert("", self.proxylog, "velocityはすでに停止しています\n")
            else:self.builder.insert("", self.mctabs[server]["txt"], f"{server}はすでに停止しています\n")
            return
        self.running_p[server].terminate()
        #self.running_p[server].kill()
        self.running_p[server] = None
    def setup(self):
        self.builder = build(app=self, folder=self.folder)
        self.pframe.grid_forget()
        self.pbar["value"] = 0
        self.pbar0["value"] = 0
        self.setuplbl.grid_forget()
        self.setuplbl["text"]="Build Velocity Server"
        self.setuplbl.grid(column=0, row=0, sticky=tk.EW, padx=10, pady=10)
        self.btn = ttk.Button(self.buildtab, text="Build", style='my.TButton', command=lambda: threading.Thread(target=self.builder.build_proxy, name="build proxy", daemon=True).start())
        self.btn.grid(column=1, row=0, padx=10, pady=10)
        servers = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(f"{self.folder}/*.json") if os.path.isdir(f"{self.folder}/{os.path.splitext(os.path.basename(x))[0]}") and os.path.basename(x)!="proxy.json"]
        if os.path.isdir(f"{self.folder}/proxy"):
            root.app.proxytab.grid(row=0, column=0, sticky=tk.NSEW)
            root.app.add(root.app.proxytab, text="proxy")
        for i in servers:
            with open(f"{self.folder}/{i}.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.addtab(name=i, software=data["software"], version=data["version"], ram=data["RAM"], bld=False)
        if os.path.isdir(f"{self.folder}/proxy") or len(servers)!=0:
            self.mcbuild()
        #mcserverのフォルダを取得してタブを作成
    def mcbuild(self):
        self.sbox = ttk.Style()
        #self.sent = ttk.Style()
        #self.sent.configure('warn.TEntry', font=FONT, bordercolor="#ff0000")
        #self.sent
        self.setuplbl["text"] = "Build Minecraft Server"
        self.btn.configure(command=self.addtab, state="enabled")
        self.namelbl = tk.Label(self.buildtab, text="Server Name", font=FONT)
        self.namelbl.grid(column=0, row=1, sticky=tk.EW, padx=10, pady=10)
        self.nameent = ttk.Entry(self.buildtab, justify=tk.CENTER, font=FONT, width=15)#, style="warn.TEntry")
        if not os.path.isdir(f"{self.folder}/lobby"):
            self.nameent.insert("end", "lobby")
        self.nameent.grid(column=1, row=1, padx=10, pady=10)
        self.nameent.focus_set()
        self.softlbl = tk.Label(self.buildtab, text="Software", font=FONT)
        self.softlbl.grid(column=0, row=2, sticky=tk.EW, padx=10, pady=10)
        self.softbox = ttk.Combobox(self.buildtab, values=["purpur", "paper"], font=FONT, state="readonly", justify=tk.CENTER, width=10)
        self.softbox.set("purpur")
        self.softbox.bind("<<ComboboxSelected>>", self.comboselect)
        self.softbox.grid(column=1, row=2, padx=10, pady=10)
        self.verlbl = tk.Label(self.buildtab, text="Minecraft Version", font=FONT)
        self.verlbl.grid(column=0, row=3, sticky=tk.EW, padx=10, pady=10)
        self.verbox = ttk.Combobox(self.buildtab, values=list(reversed(self.builder.versions["purpur"])), font=FONT, state="readonly", justify=tk.CENTER, width=10, style="my.TCombobox")
        self.verbox.set(list(reversed(self.builder.versions["purpur"]))[0])
        self.verbox.grid(column=1, row=3, padx=10, pady=10)
        self.ramlbl = tk.Label(self.buildtab, text="Memory Allocation", font=FONT)
        self.ramlbl.grid(column=0, row=4, sticky=tk.EW, padx=10, pady=10)
        self.rament = ttk.Entry(self.buildtab, justify=tk.CENTER, font=FONT, width=15)
        self.rament.insert("end", "4G")
        self.rament.grid(column=1, row=4, padx=10, pady=10)
    def addtab(self, name=None, software=None, version=None, ram=None, bld=True):
        if name==None:name = self.nameent.get()
        if software==None:software = self.softbox.get()
        if version==None:version = self.verbox.get()
        if ram==None:ram = self.rament.get()
        if name in self.mctabs:
            self.select(self.mctabs[name]["frame"])
            return
        if name == "":return
        root.app.btn["state"] = "disabled"
        self.running_p[name]=None
        self.mctabs[name] = {}
        self.mctabs[name]["frame"] = tk.Frame(self)
        self.mctabs[name]["frame"].grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)
        self.add(self.mctabs[name]["frame"], text=name)
        self.mctabs[name]["lbl"] = tk.Label(self.mctabs[name]["frame"], text="", font=FONT)
        self.mctabs[name]["lbl"].grid(column=0, row=0, sticky=tk.EW)
        self.mctabs[name]["txt"] = scrolledtext.ScrolledText(self.mctabs[name]["frame"], state="disabled", font=("Yu Gothic UI", 10, "normal"))
        self.mctabs[name]["txt"].grid(column=0, row=1, sticky=tk.NSEW)
        self.mctabs[name]["frame"].grid_rowconfigure(1, weight=1)
        self.mctabs[name]["shell"] = {}
        self.mctabs[name]["shell"]["frame"] = tk.Frame(self.mctabs[name]["frame"])
        self.mctabs[name]["shell"]["frame"].grid(column=0, row=2, sticky=tk.EW)
        self.mctabs[name]["shell"]["lbl"] = tk.Label(self.mctabs[name]["shell"]["frame"], text="Enterキーで送信", font=FONT)
        self.mctabs[name]["shell"]["lbl"].grid(column=0, row=0, sticky=tk.EW)
        self.mctabs[name]["shell"]["entry"] = tk.Entry(self.mctabs[name]["shell"]["frame"], font=FONT)
        self.mctabs[name]["shell"]["entry"].grid(column=1, row=0, sticky=tk.EW)
        self.mctabs[name]["shell"]["entry"].bind("<Return>", lambda event: self.shell(name))#TODO
        #self.mctabs[name]["shell"]["btn"] = ttk.Button(self.mctabs[name]["shell"]["frame"], text="input")
        #self.mctabs[name]["shell"]["btn"].grid(column=1, row=0)
        self.mctabs[name]["shell"]["frame"].grid_columnconfigure(1, weight=1)
        self.mctabs[name]["btnframe"] = {}
        self.mctabs[name]["btnframe"]["frame"] = tk.Frame(self.mctabs[name]["frame"])
        self.mctabs[name]["btnframe"]["frame"].grid(column=0, row=3, sticky=tk.EW)
        self.mctabs[name]["btnframe"]["run"] = ttk.Button(self.mctabs[name]["btnframe"]["frame"], text="Run", style='my.TButton', command=lambda: threading.Thread(target=lambda: self.server_runner(name), name="run").start())
        self.mctabs[name]["btnframe"]["run"].grid(column=0, row=0)
        self.mctabs[name]["btnframe"]["stop"] = ttk.Button(self.mctabs[name]["btnframe"]["frame"], text="Stop", style='my.TButton', command=lambda: self.stop(name))
        self.mctabs[name]["btnframe"]["stop"].grid(column=1, row=0)
        self.mctabs[name]["btnframe"]["kill"] = ttk.Button(self.mctabs[name]["btnframe"]["frame"], text="Kill", style='my.TButton', command=lambda: self.kill(name))
        self.mctabs[name]["btnframe"]["kill"].grid(column=2, row=0)
        self.mctabs[name]["panel"] = {}
        self.mctabs[name]["panel"]["frame"] = ttk.Frame(self.mctabs[name]["frame"])
        self.mctabs[name]["panel"]["frame"].grid(column=1, row=1, rowspan=3, sticky=tk.NSEW)
        if bld:
            self.proxyrun["state"]="disabled"
            for i in list(self.mctabs.keys()):
                self.mctabs[i]["btnframe"]["run"]["state"] = "disabled"
            threading.Thread(target=lambda: self.builder.build_mcserver(name=name, software=software, version=version, ram=ram), name="build server", daemon=True).start()
    def dlhook(self, block_count, block_size, total_size):
        dltime = time.perf_counter()-self.dlstart
        self.pbar.configure(maximum=total_size)
        dlspeed = round(block_size*block_count*8/(dltime*1024*1024), 1)
        t = round((total_size-block_size*block_count)*8/(dlspeed*1024*1024+0.01))
        self.pbar["value"] = int(block_count*block_size)
        if int(block_count*block_size/1024) > round(total_size/1024):self.progress.configure(text=f"Complete! {round(total_size/1024)}KB")
        elif (block_count*block_size/1024) != 0.0:self.progress.configure(text=f"{int(block_count*block_size/1024)}KB / {round(total_size/1024)}KB\n{dlspeed}Mbps 残り{t}s")
    def comboselect(self, event=None):
        self.verbox.configure(values=list(reversed(self.builder.versions[self.softbox.get()])))
        if not self.verbox.get() in list(reversed(self.builder.versions[self.softbox.get()])):
            self.verbox.set(list(reversed(self.builder.versions[self.softbox.get()]))[0])
    def shell(self, name, event=None):
        entry = self.mctabs[name]["shell"]["entry"].get()
        if self.running_p[name]!=None and self.running_p[name].poll()==None:
            self.running_p[name].stdin.write(entry)
            self.running_p[name].stdin.flush()
            self.mctabs[name]["txt"].see(tk.END)

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
        self.app = main(self, folder=self.folder)
        self.app.grid(row=1, column=0, sticky=tk.NSEW)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
    def dialog(self, event=None):
        self.wait_visibility()
        self.folder = filedialog.askdirectory(initialdir="./", title="Select a server directory")
        if self.folder=="" or self.folder==():
            sys.exit()

if __name__=="__main__":
    root = window()
    root.mainloop()
