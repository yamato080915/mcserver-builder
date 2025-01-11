import os, urllib.request as urllib, requests, time, shutil
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

proxy = input("Do you want to build a proxy server?(Y/n)")
if proxy=="Y" or proxy=="y":proxy = True
else:proxy = False
if proxy:
    if not os.path.isdir("proxy"):os.mkdir("proxy")
    os.chdir("proxy")
    print("The port used for the proxy server is set to 25564.")
