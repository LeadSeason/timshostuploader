import os
import sys
import traceback
import argparse
import getpass
import base64
import datetime


class pcolor:
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    NORMAL = '\033[0m'


def log(arg="", color=pcolor.NORMAL, end=""):
    print(f"{color}{arg}{pcolor.NORMAL}", end=end)


def logln(arg="", color=pcolor.NORMAL, end="\n"):
    print(f"{color}{arg}{pcolor.NORMAL}", end=end)


try:
    import requests
except ImportError:
    traceback.print_exc()
    logln("requests is needed to run this script\nhttps://pypi.org/project/requests/", pcolor.FAIL)
    sys.exit(1)

try:
    import yaml
except ImportError:
    logln("PyYaml is required to parse configuration\nhttps://pypi.org/project/PyYAML/", pcolor.FAIL)

try:
    import keyring
except ImportError:
    logln("keyring is required to store keys securly\nhttps://pypi.org/project/keyring/", pcolor.WARNING)


def save_error(message, error_log_path):
    """
        Saves error to error folder to be later examined
    """

    for i in range(sys.maxsize**10):
        filepath = f"{error_log_path}Error_{i}.log"
        if not os.path.isfile(filepath):
            with open(filepath, "w") as io:
                io.write(message)
            break


def Notification(message, submessage, icon=None):
    """
        Shows notification to user that image has been uploaded
    """
    from notifypy import Notify

    n = Notify()
    n.application_name = "FlameShot"
    n.title = message
    n.message = submessage
    if icon is not None:
        n.icon = icon
    n.send()


def save_to_file(image, url, save_path):
    """
        Saves Uploaded Image to local directory
        and names the file the upload id
    """
    filename = url[-15:] + datetime.datetime.now().strftime("_%d-%m-%Y_%H-%M-%S")
    with open(f"{save_path}{filename}.png", "wb") as io:
        io.write(image)
    return f"{save_path}{filename}.png"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--upload", help="Upload image to host", action="store_true")
    parser.add_argument("-s", "--set-key", help="Sets key into the keyring", action="store_true")
    parser.add_argument("-c", "--config", help="point to the conf file will default to ~/.config/fsuploader/fsuploader.yaml")
    parser.add_argument("-k", "--mk-conf", help="create config", action="store_true")
    args = parser.parse_args()

    if args.mk_conf irs True:
        if not os.path.isdir(os.getenv("HOME") + "/.config/fsuploader"):
            os.mkdir(os.getenv("HOME") + "/.config/fsuploader/")

        if not os.path.isfile(os.getenv("HOME") + "/.config/fsuploader/fsuploader.yaml"):
            with open(os.getenv("HOME") + "/.config/fsuploader/fsuploader.yaml", "w") as io:
                io.write(base64.b64decode("a2V5OgogICMga2V5IG9yIHRva2VuCgogICMgdGhpcyBpcyBWRVJZIElOU0VDVVJFIEFORCBET04nVCBOT1QgVVNFCiAgIyBrZXkgd2lsbCBiZSBzdG9yZWQgaGVyZSBJTiBQTEFJTiBURVhUIGFuZCBzaG91bGQgbm90IGJlIHVzZWQKICAjIGtleTogS2V5aGVyZQogIGtleXJpbmc6CiAgICAjIEtleSB3aWxsIGJlIHN0b3JlZCBpbiBrZXlyaW5nCiAgICAjIEtleXJpbmcgbW9kdWxlIHdpbGwgYmUgbmVlZGVkIHRvIHVzZSB0aGlzIGZ1bmN0aW9uYWxpdHkKICAgICMgdG8gc2V0IGtleSB1c2UgInB5dGhvbiBmc3VwbG9hZGVyLnB5IC1zIgogICAgZW5hYmxlZDogdHJ1ZQogICAgIyB3aGF0IGtleXJpbmcgdG8gYmUgdXNlZAogICAga2V5cmluZzogZGVmYXVsdAoKdXBsb2FkOgogICMgdXBsb2FkIGNvbmZpZwogIGNvbmZpZzogfi8uY29uZmlnL2ZzdXBsb2FkZXIvc2hhcmV4Y29uZi8KCnNhdmluZzoKICAjIHNhdmUgaW1hZ2UgdG8gbG9jYWwgbWFjaGluZQogIGVuYWJsZWQ6IGZhbHNlCiAgcGF0aDogfi9QaWN0dXJlcy9mc3VwbG9hZC8KICAjIG1ha2UgZGlyIGlmIGl0IGRvZXNudCBleGlzdHMKICBhdXRvbWtkaXI6IGZhbHNlCgpub3RpZmljYXRpb246CiAgIyByZXF1aXJlcyBweW5vdGlmaWNhdGlvbgogIGVuYWJsZWQ6IGZhbHNlCiAgIyBzZW5kIGVycm9ycyBpbiBub3RpZmljYXRpb25zCiAgZXJyb3JzOiBmYWxzZQoKbG9nZ2luZzoKICAjIGxvZ2Vycm9ycwogIGVuYWJsZWQ6IHRydWUKICBwYXRoOiB+Ly5jYWNoZS9mc3VwbG9hZA==".encode("ascii")).decode("ascii"))
            logln("made file ~/.config/fsuploader/fsuploader.yaml with default configuration")
        else:
            logln("Configuration file present. Please move or delete\n~/.config/fsuploader/fsuploader.yaml", pcolor.WARNING)
            sys.exit(1)

    try:
        with open(os.getenv("HOME") + "/.config/fsuploader/fsuploader.yaml") as io:
            conf = yaml.safe_load(io)
    except FileNotFoundError:
        logln("No configuration file present please run 'python fsuploader.py -k' to generate configuration file", pcolor.FAIL)
        sys.exit(1)

    if dict.get(conf["key"]["keyring"], "enabled"):
        if "keyring" in sys.modules:
            """
                Loads key from keyring or set keys
            """
            if args.set_key is True:
                key = getpass.getpass("Enter key (Will be hidden):")
                keyring.set_password("fsuploader", "pyscript", key)

            key = keyring.get_password("fsuploader", "pyscript")
    

if __name__ == "__main__":
    try:
        main()
    except Exception:
        logln("ERROR", pcolor.FAIL)
        save_error(traceback.format_exc())
