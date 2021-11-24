import os
import sys
import traceback
import argparse
import getpass
import base64
import datetime
import re


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
            print(f"saved to {filepath}")
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
    parser.add_argument("-f", "--force", help="Force", action="store_true")
    args = parser.parse_args()

    if args.mk_conf is True:
        os.mkdir(os.getenv("HOME") + "/.config/fsuploader/", exist_ok=True)

        if not os.path.isfile(os.getenv("HOME") + "/.config/fsuploader/fsuploader.yaml") or args.force:
            with open(os.getenv("HOME") + "/.config/fsuploader/fsuploader.yaml", "w") as io:
                io.write(base64.b64decode("a2V5OgogICMga2V5IG9yIHRva2VuCgogICMgdGhpcyBpcyBWRVJZIElOU0VDVVJFIEFORCBET04nVCBOT1QgVVNFCiAgIyBrZXkgd2lsbCBiZSBzdG9yZWQgaGVyZSBJTiBQTEFJTiBURVhUIGFuZCBzaG91bGQgbm90IGJlIHVzZWQKICBrZXk6IEtleWhlcmUKICBrZXlyaW5nOgogICAgIyBLZXkgd2lsbCBiZSBzdG9yZWQgaW4ga2V5cmluZwogICAgIyBLZXlyaW5nIG1vZHVsZSB3aWxsIGJlIG5lZWRlZCB0byB1c2UgdGhpcyBmdW5jdGlvbmFsaXR5CiAgICAjIHRvIHNldCBrZXkgdXNlICJweXRob24gZnN1cGxvYWRlci5weSAtcyIKICAgIGVuYWJsZWQ6IHRydWUKICAgICMgd2hhdCBrZXlyaW5nIHRvIGJlIHVzZWQKICAgIGtleXJpbmc6IGRlZmF1bHQKCnVwbG9hZDoKICAjIHVwbG9hZCBjb25maWcKICBjb25maWc6IH4vLmNvbmZpZy9mc3VwbG9hZGVyL3VwY29uZi9jb25maWcuanNvbgoKc2F2aW5nOgogICMgc2F2ZSBpbWFnZSB0byBsb2NhbCBtYWNoaW5lCiAgZW5hYmxlZDogZmFsc2UKICBwYXRoOiB+L1BpY3R1cmVzL2ZzdXBsb2FkLwogICMgbWFrZSBkaXIgaWYgaXQgZG9lc250IGV4aXN0cwogIGF1dG9ta2RpcjogZmFsc2UKCm5vdGlmaWNhdGlvbjoKICAjIHJlcXVpcmVzIHB5bm90aWZpY2F0aW9uCiAgZW5hYmxlZDogZmFsc2UKICAjIHNlbmQgZXJyb3JzIGluIG5vdGlmaWNhdGlvbnMKICBlcnJvcnM6IGZhbHNlCgpsb2dnaW5nOgogICMgbG9nZXJyb3JzCiAgZW5hYmxlZDogdHJ1ZQogIHBhdGg6IH4vLmNhY2hlL2ZzdXBsb2Fk".encode("ascii")).decode("ascii"))
            logln("made file ~/.config/fsuploader/fsuploader.yaml with default configuration")
        else:
            logln("Configuration file present. Please move or delete\n~/.config/fsuploader/fsuploader.yaml\nor use -f flag to force replacement", pcolor.WARNING)
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
        traceback.print_exc()
        try:
            with open(os.getenv("HOME") + "/.config/fsuploader/fsuploader.yaml") as io:
                conf = yaml.safe_load(io)
        except FileNotFoundError:
            logln("Configuration file not detected\nsaving error in ~/.cache/fsuploader", pcolor.FAIL)
            errorenabled = True
            errorsavepath = open(os.getenv("HOME") + "/.cache/fsuploader/")

        else:
            if dict.get(conf, "logging"):
                if dict.get(conf["logging"], "enabled"):
                    if not dict.get(conf["logging"], "path") is None:
                        errorsavepath = dict.get(conf["logging"], "path")
                        if not errorsavepath.endswith("/"):
                            errorsavepath += "/"
                        if errorsavepath.startswith("~"):
                            errorsavepath = errorsavepath.replace("~", os.getenv("HOME"), 1)
                    else:
                        errorsavepath = os.getenv("HOME") + "/.cache/fsuploader/"
                else:
                    logln("error login disabled. error will not be saved")
                    sys.exit(2)

        os.makedirs(errorsavepath, exist_ok=True)
        save_error(traceback.format_exc(), errorsavepath)
