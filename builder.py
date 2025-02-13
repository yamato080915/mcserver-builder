import os, requests, shutil, json, subprocess, sys, yaml, toml, platform
from tqdm import tqdm

urls = {
    "updater": "https://github.com/yamato080915/mcserver-updater/archive/refs/heads/main.zip", 
    "purpur": "https://api.purpurmc.org/v2/purpur/"
}
jdkurls = {
    "Windows": [
        ["jdk21", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/21.0.5+11/openlogic-openjdk-21.0.5+11-windows-x64.zip", "openlogic-openjdk-21.0.5+11-windows-x64"], 
        ["jdk17", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/17.0.13+11/openlogic-openjdk-17.0.13+11-windows-x64.zip", "openlogic-openjdk-17.0.13+11-windows-x64"], 
        ["jdk11", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/11.0.25+9/openlogic-openjdk-11.0.25+9-windows-x64.zip", "openlogic-openjdk-11.0.25+9-windows-x64"],
        ["jdk8", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/8u432-b06/openlogic-openjdk-8u432-b06-windows-x64.zip", "openlogic-openjdk-8u432-b06-windows-x64"]
        ], 
    "Linux":[
        ["jdk21", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/21.0.5+11/openlogic-openjdk-21.0.5+11-linux-x64.tar.gz", "openlogic-openjdk-21.0.5+11-linux-x64"], 
        ["jdk17", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/17.0.13+11/openlogic-openjdk-17.0.13+11-linux-x64.tar.gz", "openlogic-openjdk-17.0.13+11-linux-x64"], 
        ["jdk11", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/11.0.25+9/openlogic-openjdk-11.0.25+9-linux-x64.tar.gz", "openlogic-openjdk-11.0.25+9-linux-x64"],
        ["jdk8", "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/8u432-b06/openlogic-openjdk-8u432-b06-linux-x64.tar.gz", "openlogic-openjdk-8u432-b06-linux-x64"]
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
    def install(self):
        for i in tqdm(urls["jdk"], total=len(urls["jdk"]), desc="jdk", unit="files"):
            if not os.path.isdir(f"jdk/{i[0]}"):
                r = requests.get(i[1], stream=True)
                with open(f"__cache__/{i[0]}.{"zip" if OS=="Windows" else "tar.gz"}", "wb") as f:
                    for chunk in tqdm(r.iter_content(chunk_size=1024), total=round(int(r.headers.get("content-length", -1))/1024), unit="KB", desc=i[2], leave=False):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                shutil.unpack_archive(f"__cache__/{i[0]}.{"zip" if OS=="Windows" else "tar.gz"}", "jdk")
                shutil.move(f"./jdk/{i[2]}", f"./jdk/{i[0]}")
        if os.path.isfile("updater.py"):print("updating mcserver-updater")
        else:print("installing mcserver-updater")
        with open("__cache__/updater.zip", "wb") as f:
            f.write(requests.get(urls["updater"]).content)
        shutil.unpack_archive("__cache__/updater.zip", "./__cache__")
        shutil.move("__cache__/mcserver-updater-main/main.py", "./updater.py")
        shutil.move("__cache__/mcserver-updater-main/README.md", "./README.md")
    def build_proxy(self):
        if self.proxy:return
        if not os.path.isdir("proxy"):os.mkdir("proxy")
        self.jsonData = {"file": "./proxy/server.jar", "software": "velocity", "version": "", "build": 0, "jdk": "..\\jdk\\jdk21\\bin\\java".replace("\\","/" if OS!="Windows" else "\\"), "RAM": "512M"}
        with open("proxy.json", "w", encoding="utf-8") as f:
            json.dump(self.jsonData, f, indent=4)
        cmdData = "@echo off\npy updater.py proxy.json\nIF %ERRORLEVEL% == 0 (\n    cd proxy\n    ..\\jdk\\jdk21\\bin\\java -Xmx512M -Xms512M -jar server.jar nogui\n    pause\n) ELSE (\n    echo %ERRORLEVEL%\n    pause\n)"
        with open("./proxy.cmd", "w", encoding="utf-8") as f:
            f.write(cmdData)
        p = subprocess.Popen([pypath, "updater.py", "proxy.json"])
        p.wait()
        os.chdir("proxy")
        p = subprocess.Popen(["..\\jdk\\jdk21\\bin\\java".replace("\\", "/" if OS!="Windows" else "\\"), "-Xmx512M", "-Xms512M", "-jar", "server.jar"], stdin=subprocess.PIPE, shell=OS=="Windows")
        p.communicate(input="end".encode())
        self.proxy = True
    def proxy_setting(self):
        velocity = toml.load(open("velocity.toml"))
        velocity["player-info-forwarding-mode"] = "modern"
        velocity["force-key-authentication"] = False
        velocity["servers"] = {}
        velocity["forced-hosts"] = {}
        toml.dump(velocity, open('velocity.toml', mode='w'))
    def forward(self):
        with open("forwarding.secret", "r", encoding="utf-8") as f:
            self.secret = f.read()
    def build_mcserver(self, name="lobby", version="", ram="4G"):
        os.chdir(self.cwd)
        if version=="":version = self.versions[-1]
        self.path = "..\\jdk\\jdk21\\bin\\java" if version in self.jdkpath["..\\jdk\\jdk21\\bin\\java"] else "..\\jdk\\jdk17\\bin\\java" if version in self.jdkpath["..\\jdk\\jdk17\\bin\\java"] else "..\\jdk\\jdk11\\bin\\java"
        if OS!="Windows":self.path = self.path.replace("\\", "/")
        self.jsonData = {"file": f"{name}/purpur.jar", "software": "purpur", "version": version, "build": 0, "version-up": False, "jdk": self.path, "RAM": ram}
        with open(f"{name}.json", "w", encoding="utf-8") as f:
            json.dump(self.jsonData, f, indent=4)
        cmdData = f"@echo off\npy updater.py {name}.json\nIF %ERRORLEVEL% == 0 (\n    cd {name}\n    {self.path} -Xmx4G -Xms4G -jar purpur.jar nogui\n    pause\n) ELSE (\n    echo %ERRORLEVEL%\n    pause\n)"
        with open(f"./{name}.cmd", "w", encoding="utf-8") as f:
            f.write(cmdData)
        if not os.path.isdir(name):os.mkdir(name)
        with open(f"{name}/eula.txt", "w", encoding="utf-8") as f:
            f.write("eula=true")
        p = subprocess.Popen([pypath, "updater.py", f"{name}.json"])
        p.wait()
        os.chdir(name)
        p = subprocess.Popen([self.path, f"-Xmx{ram}", f"-Xms{ram}", "-jar", "purpur.jar", "nogui"], stdin=subprocess.PIPE, shell=OS=="Windows")
        p.communicate(input="stop".encode())
        p.wait()
    def velocity_setting(self, name="lobby"):
        if not self.proxy:return
        with open("server.properties", "r", encoding="utf-8") as f:
            properties = f.read().splitlines()
        text = ""
        for i, e in enumerate(properties):
            if "online-mode" in e:
                properties[i] = "online-mode=false"
                print("set online-mode=false")
            text += f"\n{properties[i]}"
        with open("server.properties", "w", encoding="utf-8") as f:
            f.write(text)
        if os.path.isfile("paper.yml"):yml = "paper.yml"
        else:yml = "config/paper-global.yml"
        with open(yml, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        print("set paper.yml")
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
                print(f"set {name} port:{25565 + 1 if len(list(velocity["servers"].values()))==2 else len(list(velocity["servers"].values()))}")
            text += f"\n{properties[i]}"
        with open("server.properties", "w", encoding="utf-8") as f:
            f.write(text)
        
if __name__=="__main__":
    main = build()
    main.build_proxy()
    main.proxy_setting()
    main.forward()
    main.build_mcserver()
    main.velocity_setting()
    print(main.secret)