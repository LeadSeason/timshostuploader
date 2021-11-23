import os
import sys
import traceback
import argparse
import getpass


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
    sys.exit(1)

try:
    import keyring
except ImportError:
    logln("keyring is required to store keys securly\nhttps://pypi.org/project/keyring/", pcolor.WARNING)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--upload", help="Upload image to host", action="store_true")
    parser.add_argument("-S", "--set-key", help="Sets key intothe keyring")
    parser.add_argument("-c", "--config", help="point to the conf file will default to ~/.config/fsuploader.yaml")
    args = parser.parse_args()
    print(args)

    if "keyring" in sys.modules:
        """
            Loads key from keyring or set keys
        """
        print(keyring.get_password("fsuploader", "pyscript"))
        if args.set_key is not None:
            # if args.set_key is True:
            #     key = getpass.getpass("Enter key (Will be hidden):")
            # else:
            #     key = args.set_key
            keyring.set_password("fsuploader", "pyscript", args.set_key)





if __name__ == "__main__":
    main()
