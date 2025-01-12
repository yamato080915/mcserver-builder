import os, requests, shutil, json, subprocess, sys, yaml

urls = {
    "updater": "https://github.com/yamato080915/mcserver-updater/archive/refs/heads/main.zip"
}
if not os.name == "nt":
    sys.exit("Unsupported OS")

folder = input("server folder:")
if not os.path.isdir(folder):
    os.mkdir(folder)
os.chdir(folder)

cwd = os.getcwd()

if os.path.isfile("updater.py"):print("updating mcserver-updater")
else:print("installing mcserver-updater")
if not os.path.isdir("__cache__"):
    os.mkdir("__cache__")

with open("__cache__/updater.zip", "wb") as f:
    f.write(requests.get(urls["updater"]).content)
shutil.unpack_archive("__cache__/updater.zip", "./__cache__")
shutil.move("__cache__/mcserver-updater-main/main.py", "./updater.py")
shutil.move("__cache__/mcserver-updater-main/README.md", "./README.md")

if os.path.isdir("proxy") and os.path.isfile("proxy/forwarding.secret"):
    proxy = True
else:
    proxy = input("Do you want to build a proxy server?(Default Y)(Y/n)")
    if proxy.upper()=="Y" or proxy == "":proxy = True
    else:proxy = False
    if proxy:
        if not os.path.isdir("proxy"):os.mkdir("proxy")
        jsonData = {"file": "./proxy/server.jar", "software": "velocity", "version": "", "build": 0}
        with open("proxy.json", "w", encoding="utf-8") as f:
            json.dump(jsonData, f, indent=4)
        cmdData = "@echo off\npy updater.py proxy.json\nIF %ERRORLEVEL% == 0 (\n    cd proxy\n    java -Xmx512M -Xms512M -jar server.jar nogui\n    pause\n) ELSE (\n    echo %ERRORLEVEL%\n    pause\n)"
        with open("./proxy.cmd", "w", encoding="utf-8") as f:
            f.write(cmdData)
        p = subprocess.Popen(["py", "updater.py", "proxy.json"])
        p.wait()
        os.chdir("proxy")
        p = subprocess.Popen(["java", "-Xmx512M", "-Xms512M", "-jar", "server.jar"], stdin=subprocess.PIPE, shell=True)
        p.communicate(input="end".encode())
        with open("velocity.toml", "r", encoding="utf-8") as f:
            velocity = f.read().splitlines()
        text = ""
        for i, e in enumerate(velocity):
            if "player-info-forwarding-mode" in e:
                velocity[i] = 'player-info-forwarding-mode = "modern"'
                print('set player-info-forwarding-mode = "modern"')
            elif "force-key-authentication" in e:
                velocity[i] = "force-key-authentication = false"
                print("set force-key-authentication = false")
            text += f"\n{velocity[i]}"
        with open("velocity.toml", "w", encoding="utf-8") as f:
            f.write(text)

with open("forwarding.secret", "r", encoding="utf-8") as f:
    secret = f.read()

def add_server():
    os.chdir(cwd)
    servername = input("server name(default lobby):")
    if servername == "":servername = "lobby"
    version = input("minecraft version(default latest):")
    jsonData = {"file": f"{servername}/purpur.jar", "software": "purpur", "version": version, "build": 0, "version-up": True if version=="" or version=="latest" else False}
    with open(f"{servername}.json", "w", encoding="utf-8") as f:
        json.dump(jsonData, f, indent=4)
    cmdData = f"@echo off\npy updater.py {servername}.json\nIF %ERRORLEVEL% == 0 (\n    cd {servername}\n    java -Xmx4G -Xms4G -jar server.jar nogui\n    pause\n) ELSE (\n    echo %ERRORLEVEL%\n    pause\n)"
    with open(f"./{servername}.cmd", "w", encoding="utf-8") as f:
        f.write(cmdData)
    if not os.path.isdir(servername):os.mkdir(servername)
    with open(f"{servername}/eula.txt", "w", encoding="utf-8") as f:
        f.write("eula=true")
    p = subprocess.Popen(["py", "updater.py", f"{servername}.json"])
    p.wait()
    os.chdir(servername)
    p = subprocess.Popen(["java", "-Xmx4G", "-Xms4G", "-jar", "purpur.jar", "nogui"], stdin=subprocess.PIPE, shell=True)
    p.communicate(input="stop".encode())
    with open("server.properties", "r", encoding="utf-8") as f:
        properties = f.read().splitlines()
    text = ""
    for i, e in enumerate(properties):
        if "online-mode" in e:
            properties[i] = "online-mode=false"
            print("set online-mode=false")
        text += f"{properties[i]}"
    with open("server.properties", "w", encoding="utf-8") as f:
        f.write(text)
    if os.path.isfile("paper.yml"):yml = "paper.yml"
    else:yml = "config/paper-global.yml"
    with open(yml, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    config["proxies"]["velocity"]["enabled"] = True
    config["proxies"]["velocity"]["online-mode"] = True

#"config/paper-global.yml" or "paper.yml"#TODO
add_server()