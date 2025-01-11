import os, urllib.request as urllib, requests, time, shutil, json
from tqdm import tqdm

bar = ""
def reporthook(block, bs, size):
    if size <=0:return
    bar.total = size
    bar.update(block*bs if block*bs<=size else size)

urls = {
    "updater": "https://github.com/yamato080915/mcserver-updater/archive/refs/heads/main.zip"
}

folder = input("server folder:")
if not os.path.isdir(folder):
    os.mkdir(folder)
os.chdir(folder)

cwd = os.getcwd()

print("installing mcserver-updater")
if not os.path.isdir("__cache__"):
    os.mkdir("__cache__")

urllib.urlretrieve(filename="__cache__/updater.zip", url=urls["updater"])
shutil.unpack_archive("__cache__/updater.zip", "./__cache__")
shutil.move("__cache__/mcserver-updater-main/main.py", "./updater.py")
shutil.move("__cache__/mcserver-updater-main/README.md", "./")

proxy = input("Do you want to build a proxy server?(Y/n)")
if proxy=="Y" or proxy=="y":proxy = True
else:proxy = False
if proxy:
    if not os.path.isdir("proxy"):os.mkdir("proxy")
    jsonData = {"file": "./proxy/server.jar", "software": "velocity", "version": "", "build": 0}
    with open("proxy.json", "w", encoding="utf-8") as f:
        json.dump(jsonData, f, indent=4)
    cmdData = "@echo off\npython updater.py proxy.json\nIF %ERRORLEVEL% == 0 (\n    java -Xmx512M -Xms512M -jar proxy/server.jar --nogui\n    pause\n) ELSE (\n    echo %ERRORLEVEL%\n    pause\n)"
    with open("./proxy.cmd", "w", encoding="utf-8") as f:
        f.write(cmdData)
    print("The port used for the proxy server is set to 25564.")
