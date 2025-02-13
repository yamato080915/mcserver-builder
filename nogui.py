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

folder = input("server folder:")
if not os.path.isdir(folder):os.mkdir(folder)
os.chdir(folder)
cwd = os.getcwd()

if not os.path.isdir("__cache__"):os.mkdir("__cache__")
if not os.path.isdir("jdk"):os.mkdir("jdk")

for i in tqdm(urls["jdk"], total=4, desc="jdk", unit="files"):
    if not os.path.isdir(f"jdk/{i[0]}"):
        r = requests.get(i[1], stream=True)
        with open(f"__cache__/{i[0]}.{"zip" if OS=="Windows" else "tar.gz"}", "wb") as f:
            for chunk in tqdm(r.iter_content(chunk_size=1024), total=round(int(r.headers.get('content-length', -1))/(1024)), unit="KB", desc=i[2], leave=False):
                if chunk:
                    f.write(chunk)
                    f.flush()
        shutil.unpack_archive(f"__cache__/{i[0]}.{"zip" if OS=="Windows" else "tar.gz"}", "jdk")
        shutil.move(f"./jdk/{i[2]}", f"./jdk/{i[0]}")

shutil.rmtree("__cache__")
os.mkdir("__cache__")

versions = list(json.loads(requests.get(urls["purpur"]).text)["versions"])
jdkpath = {"..\\jdk\\jdk11\\bin\\java": versions[:versions.index("1.16.5")+1], "..\\jdk\\jdk17\\bin\\java": versions[versions.index("1.16.5")+1:versions.index("1.19.2")+1], "..\\jdk\\jdk21\\bin\\java": versions[versions.index("1.19.3"):]}

if os.path.isfile("updater.py"):print("updating mcserver-updater")
else:print("installing mcserver-updater")

with open("__cache__/updater.zip", "wb") as f:
    f.write(requests.get(urls["updater"]).content)
shutil.unpack_archive("__cache__/updater.zip", "./__cache__")
shutil.move("__cache__/mcserver-updater-main/main.py", "./updater.py")
shutil.move("__cache__/mcserver-updater-main/README.md", "./README.md")

if os.path.isdir("proxy") and os.path.isfile("proxy/forwarding.secret"):
    proxy = True
    os.chdir("proxy")
else:
    proxy = input("Do you want to build a proxy server?(Default Y)(Y/n)")
    if proxy.upper()=="Y" or proxy == "":proxy = True
    else:proxy = False
    if proxy:
        if not os.path.isdir("proxy"):os.mkdir("proxy")
        jsonData = {"file": "./proxy/server.jar", "software": "velocity", "version": "", "build": 0, "jdk": "..\\jdk\\jdk21\\bin\\java".replace("\\","/" if OS!="Windows" else "\\"), "RAM": "512M"}
        with open("proxy.json", "w", encoding="utf-8") as f:
            json.dump(jsonData, f, indent=4)
        cmdData = "@echo off\npy updater.py proxy.json\nIF %ERRORLEVEL% == 0 (\n    cd proxy\n    ..\\jdk\\jdk21\\bin\\java -Xmx512M -Xms512M -jar server.jar nogui\n    pause\n) ELSE (\n    echo %ERRORLEVEL%\n    pause\n)"
        with open("./proxy.cmd", "w", encoding="utf-8") as f:
            f.write(cmdData)
        p = subprocess.Popen([pypath, "updater.py", "proxy.json"])
        p.wait()
        os.chdir("proxy")
        p = subprocess.Popen(["..\\jdk\\jdk21\\bin\\java".replace("\\", "/" if OS!="Windows" else "\\"), "-Xmx512M", "-Xms512M", "-jar", "server.jar"], stdin=subprocess.PIPE, shell=OS=="Windows")
        p.communicate(input="end".encode())
        velocity = toml.load(open("velocity.toml"))
        velocity["player-info-forwarding-mode"] = "modern"
        velocity["force-key-authentication"] = False
        velocity["servers"] = {}
        velocity["forced-hosts"] = {}
        toml.dump(velocity, open('velocity.toml', mode='w'))
if proxy:
    with open("forwarding.secret", "r", encoding="utf-8") as f:
        secret = f.read()
else:secret = ""

def add_server():
    os.chdir(cwd)
    servername = input("server name(default lobby):")
    if servername == "":servername = "lobby"
    version = input("minecraft version(default latest):")
    if version=="latest":version = ""
    jsonData = {"file": f"{servername}/purpur.jar", "software": "purpur", "version": version, "build": 0, "version-up": True if version=="" else False}
    if version == "":version = versions[-1]
    path = "..\\jdk\\jdk21\\bin\\java" if version in jdkpath["..\\jdk\\jdk21\\bin\\java"] else "..\\jdk\\jdk17\\bin\\java" if version in jdkpath["..\\jdk\\jdk17\\bin\\java"] else "..\\jdk\\jdk11\\bin\\java"
    if OS!="Windows":path = path.replace("\\", "/")
    jsonData["jdk"] = path
    jsonData["RAM"] = "4G"
    with open(f"{servername}.json", "w", encoding="utf-8") as f:
        json.dump(jsonData, f, indent=4)
    cmdData = f"@echo off\npy updater.py {servername}.json\nIF %ERRORLEVEL% == 0 (\n    cd {servername}\n    {path} -Xmx4G -Xms4G -jar purpur.jar nogui\n    pause\n) ELSE (\n    echo %ERRORLEVEL%\n    pause\n)"
    with open(f"./{servername}.cmd", "w", encoding="utf-8") as f:
        f.write(cmdData)
    if not os.path.isdir(servername):os.mkdir(servername)
    with open(f"{servername}/eula.txt", "w", encoding="utf-8") as f:
        f.write("eula=true")
    p = subprocess.Popen([pypath, "updater.py", f"{servername}.json"])
    p.wait()
    os.chdir(servername)
    p = subprocess.Popen([path, "-Xmx4G", "-Xms4G", "-jar", "purpur.jar", "nogui"], stdin=subprocess.PIPE, shell=OS=="Windows")
    p.communicate(input="stop".encode())
    p.wait()
    if proxy:
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
        if yml == "paper.yml":
            config["settings"]["velocity-support"]["enabled"] = True
            config["settings"]["velocity-support"]["online-mode"] = True
            config["settings"]["velocity-support"]["secret"] = secret
        else:
            config["proxies"]["velocity"]["enabled"] = True
            config["proxies"]["velocity"]["online-mode"] = True
            config["proxies"]["velocity"]["secret"] = secret
        with open(yml, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f)
        os.chdir("../proxy")
        velocity = toml.load(open("velocity.toml"))
        if [] == list(velocity["servers"].values()):
            velocity["servers"][servername] = "127.0.0.1:25566"
            velocity["servers"]["try"] = [servername]
        else:
            velocity["servers"][servername] = f"127.0.0.1:{25565 + len(list(velocity["servers"].values()))}"
        toml.dump(velocity, open('velocity.toml', mode='w'))
        os.chdir(f"../{servername}")
        text = ""
        for i, e in enumerate(properties):
            if "server-port" in e:
                properties[i] = f"server-port={25565 + 1 if len(list(velocity["servers"].values()))==2 else len(list(velocity["servers"].values()))}"
                print(f"set {servername} port:{25565 + 1 if len(list(velocity["servers"].values()))==2 else len(list(velocity["servers"].values()))}")
            text += f"\n{properties[i]}"
        with open("server.properties", "w", encoding="utf-8") as f:
            f.write(text)

add_server()
