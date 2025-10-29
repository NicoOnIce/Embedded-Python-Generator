import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import urllib.request
import zipfile
import shutil
import os

def downloadPython(version, arch, log):
    url = f"https://www.python.org/ftp/python/{version}/python-{version}-embed-{arch}.zip"
    log(f"Downloading {url}\n")
    urllib.request.urlretrieve(url, "python.zip")
    log("Download complete!\n")

def buildEmbeddedPython(version, arch, packages, buildType, log):
    try:
        for folder in ["build", "dist"]:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                log(f"Removed old folder: {folder}\n")

        if buildType == "external":
            downloadPython(version, arch, log)
        else:
            if os.path.exists("python.zip"):
                log("Using existing python.zip\n")
            else:
                messagebox.showerror("Error", "python.zip not found for local build.")
                return

        log("Extracting python.zip...\n")
        with zipfile.ZipFile("python.zip", "r") as zipRef:
            zipRef.extractall("dist")

        os.makedirs("dist/Lib/site-packages", exist_ok=True)

        vShort = "".join(version.split(".")[:2])
        pthFile = f"dist/python{vShort}._pth"
        with open(pthFile, "a") as file:
            file.write("import site\n")
        log("Enabled 'import site' in embedded Python.\n")

        log("Creating temporary venv...\n")
        subprocess.run("python -m venv build", shell=True, check=True)
        log("Activating venv and installing packages...\n")

        if packages.strip():
            cmd = f'cmd /c "call build\\Scripts\\activate.bat && pip install {packages}"'
            subprocess.run(cmd, shell=True, check=True)
            log(f"Installed packages: {packages}\n")

        src = "build/Lib/site-packages"
        dst = "dist/Lib/site-packages"
        if os.path.exists(src):
            for entry in os.scandir(src):
                if "pip" not in entry.name:
                    target = os.path.join(dst, entry.name)
                    if entry.is_dir():
                        shutil.copytree(entry.path, target, dirs_exist_ok=True)
                    else:
                        shutil.copy(entry.path, target)
                    log(f"Copied {entry.name}\n")

        log("\nBuild complete!\nCheck the 'dist' folder.\n")

    except Exception as e:
        log(f"\nError: {e}\n")
        messagebox.showerror("Error", str(e))

def startBuild():
    version = versionVar.get()
    arch = archVar.get()
    buildType = buildTypeVar.get()
    packages = packagesEntry.get()

    if not version or not arch:
        messagebox.showwarning("Missing Info", "Please select version and architecture.")
        return

    buildButton.config(state="disabled")
    logText.delete("1.0", tk.END)

    def run():
        buildEmbeddedPython(version, arch, packages, buildType, log=lambda msg: logText.insert(tk.END, msg))
        buildButton.config(state="normal")

    threading.Thread(target=run, daemon=True).start()

root = tk.Tk()
root.title("Python Embed Installer")
root.geometry("700x500")

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.X)

ttk.Label(frame, text="Python Version:").grid(row=0, column=0, sticky=tk.W)
versionVar = tk.StringVar(value="3.14.0")
versionList = ["3.12.6", "3.13.1", "3.14.0"]
ttk.Combobox(frame, textvariable=versionVar, values=versionList, width=10).grid(row=0, column=1)

ttk.Label(frame, text="Architecture:").grid(row=0, column=2, padx=(20, 0))
archVar = tk.StringVar(value="amd64")
archList = ["amd64", "win32", "arm64"]
ttk.Combobox(frame, textvariable=archVar, values=archList, width=8).grid(row=0, column=3)

ttk.Label(frame, text="Type:").grid(row=0, column=4, padx=(20, 0))
buildTypeVar = tk.StringVar(value="local")
typeList = ["local", "external"]
ttk.Combobox(frame, textvariable=buildTypeVar, values=typeList, width=8).grid(row=0, column=5)

ttk.Label(frame, text="Packages:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
packagesEntry = ttk.Entry(frame, width=50)
packagesEntry.grid(row=1, column=1, columnspan=5, sticky=tk.W, pady=(10, 0))

buildButton = ttk.Button(frame, text="Build", command=startBuild)
buildButton.grid(row=2, column=0, columnspan=6, pady=(15, 0))

logText = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20)
logText.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.mainloop()
