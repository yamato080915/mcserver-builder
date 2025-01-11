import os, sys

def getos():
	temp = dict(os.environ)
	if "DESKTOP_SESSION" in temp:OS=temp["DESKTOP_SESSION"]
	elif "OS" in temp:OS="Windows"
	else:OS="unknown OS"
	return OS
