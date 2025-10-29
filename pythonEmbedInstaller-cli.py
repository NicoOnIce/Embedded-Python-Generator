import subprocess
import argparse
import zipfile
import shutil
import time
import sys
import os

import urllib.request

parser = argparse.ArgumentParser(description="My portable Python app")

parser.add_argument("--type", type=str, default="local", help="If your installation is local or external")

parser.add_argument("--version", type=str, default="3.14.0", help="Version")
parser.add_argument("--arch", type=str, default="amd64", help="Desired architecture for install")

parser.add_argument("--name", type=str, default="python.zip", help="Directory to zip embeded zip")

parser.add_argument("--packages", type=str, default="", help="Packages you want to add, split by spaces")

args = parser.parse_args()

if not args.type:
    input("Err: No type parsed. Run this application with \"--t <TYPE>\". TYPE can be local or external.\n[ENTER TO EXIT]")
    sys.exit()

def downloadPythonVersion(version, arch):
    urllib.request.urlretrieve(
        f"https://www.python.org/ftp/python/{version}/python-{version}-embed-{arch}.zip", 
        "python.zip"
    )

def main():
    if args.type == "external":
        print("External python version must be downloaded to continue.")
        if input("Do you want to continue? y/n\n") == "y":
            print("Downloading python...")
            downloadPythonVersion(args.version, args.arch)
        else:
            input("Err: cannot conintue process\n[ENTER TO EXIT]")
            sys.exit()
    else:
        print("Renaming .zip file to python.zip...")
        os.rename(args.name, "python.zip")

    try:
        shutil.rmtree("build")
    except:
        pass

    try:
        shutil.rmtree("dist")
    except:
        pass

    print("Unzipping folder...")
    with zipfile.ZipFile("python.zip", 'r') as zip_ref:
        zip_ref.extractall("dist")

    os.mkdir("dist\\Lib")
    os.mkdir("dist\\Lib\\site-packages")

    v = args.version.split(".")
    v.pop(-1)
    with open(f"dist\\python{''.join(v)}._pth", "r") as file:
        lines = file.readlines()
        lines.append("import site\n")

    with open(f"dist\\python{''.join(v)}._pth", "w") as file:
        file.writelines(lines)

    print("Creating new build directory...")
    os.mkdir("build")
    
    commands = [
        "python -m venv build",
        "call build\\Scripts\\activate.bat"
    ]

    if args.packages != []:
        commands.append(f"pip install {args.packages}")
    
    proc = subprocess.Popen("cmd", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for command in commands:
        print("Running command:", command)

        proc.stdin.write(f"{command}\n")
        proc.stdin.flush()

        if "pip install" in command:
            output, errors = proc.communicate()
        else:
            time.sleep(1)
        
    print("Moving necassary package files to embeded python...")
    with os.scandir("build\\Lib\\site-packages") as entries:
        for entry in entries:
            if "pip" not in entry.name:
                print("Moving entry:", entry.name)
                if entry.is_file():
                    shutil.copy(entry.path, "dist\\Lib\\site-packages")
                elif entry.is_dir():
                    shutil.copytree(entry.path, f"dist\\Lib\\site-packages\\{entry.name}")
    
    print("\nFinished building portable folder!")
    print("Test it before release.")
    input("[ENTER TO EXIT]")

if __name__ == "__main__":
    main()
