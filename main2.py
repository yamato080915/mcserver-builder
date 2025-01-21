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
    def __init__(self, folder):
        self.folder = folder
        self.proxy = True
        self.servername = "lobby"
        self.version = ""
        self.setup(folder)
        self.install()
        shutil.rmtree("__cache__")
        os.mkdir("__cache__")
        self.versions = list(json.loads(requests.get(urls["purpur"]).text)["versions"])
        self.jdkpath = {"..\\jdk\\jdk11\\bin\\java": versions[:versions.index("1.16.5")+1], "..\\jdk\\jdk17\\bin\\java": versions[versions.index("1.16.5")+1:versions.index("1.19.2")+1], "..\\jdk\\jdk21\\bin\\java": versions[versions.index("1.19.3"):]}
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

if __name__=="__main__":
    main = build("server")