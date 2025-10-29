# Embedded-Python-Generator
Allows the user to create an embedded version of python, either through a CLI, or a GUI.

## Requirements
- Windows operating system
- Python installed, and in PATH
- pip installed, and in PATH

## How To Use
- Download either the CLI or GUI Python script
- Ensure your cmd's working directory is the same as the downloaded Python script.
- If using CLI, run the command `python pythonEmbedInstaller-cli.py --type external --version <VER.SIO.N> --arch <ARCHITECTURE> --packages "<PACKAGES>"`.
- Example of running CLI command `python main.py --type external --version 3.14.0 --arch amd64 --packages "requests cryptography rich prompt_toolkit"`
- If using GUI, run the script as you would any other python script and fill the fields provided.
