import re
import sys
from hashlib import md5
from urllib.request import urlopen
from typing import Tuple, Optional
from otlet import PackageObject
import threading

# The following regex patterns were taken/modified from version 1.4.1 of the 'wheel_filename' package
# located at 'https://github.com/jwodder/wheel-filename'.
WHLRGX = re.compile(
    r"(?P<project>[A-Za-z0-9](?:[A-Za-z0-9._]*[A-Za-z0-9])?)"
    r"-(?P<version>[A-Za-z0-9_.!+]+)"
    r"(?:-(?P<build>[0-9][\w\d.]*))?"
    r"-(?P<python_tags>[\w\d]+(?:\.[\w\d]+)*)"
    r"-(?P<abi_tags>[\w\d]+(?:\.[\w\d]+)*)"
    r"-(?P<platform_tags>[\w\d]+(?:\.[\w\d]+)*)"
    r"\.[Ww][Hh][Ll]"
)
TAGRGX = re.compile(
    r"(?:(?P<build>[0-9\*][\w\d.]*))?"
    r"-(?P<python_tags>[\w\d\*]+(?:\.[\w\d]+)*)"
    r"-(?P<abi_tags>[\w\d\*]+(?:\.[\w\d]+)*)"
    r"-(?P<platform_tags>[\w\d\*]+(?:\.[\w\d]+)*)"
)
msg_board = {
    "_download": {
        "bytes_read": 0
    }
}

def _download(url: str, dest: str) -> None:
    """Download a binary file from a given URL. Do not use this function directly."""
    # download file and store bytes
    msg_board["_download"]["status"] = -1
    request_obj = urlopen(url)
    f = open(dest, "wb")
    ONE_MB = 1048576
    while True:
        j = request_obj.read(ONE_MB) # read one 1M chunk at a time
        if j == b'':
            break
        f.write(j)
        msg_board["_download"]["bytes_read"] += ONE_MB
    f.close()

    # enforce that we downloaded the correct file, and no corruption took place
    with open(dest, 'rb') as f:
        data_hash = md5(f.read()).hexdigest()
    cloud_hash = request_obj.headers["ETag"].strip('"')
    if data_hash != cloud_hash:
        msg_board["_download"]["error"] = "The file was corrupted during download. Please try again..."
        msg_board["_download"]["status"] = 1
        return

    msg_board["_download"]["status"] = 0


def download_dist(
    pkg: PackageObject,
    dest: str,
    whl_format: Optional[str] = None,
    dist_type: Optional[str] = None
) -> int:
    """
    Download a specified package's distribution file.
    """

    if dist_type is None:
        dist_type = "bdist_wheel"

    if dist_type != "bdist_wheel" and whl_format:
        print(
            f"Specified custom .whl format, but requested '{dist_type}'. Ignoring...",
            file=sys.stderr,
        )

    if dist_type == "bdist_wheel":
        if whl_format is None:
            whl_format = "*-*-*-*"
        _whl_format = TAGRGX.match(whl_format)
        if _whl_format is None:
            print(
                "Improper format used. Should be '{build_tag}-{python_tag}-{abi_tag}-{platform_tag}'",
                file=sys.stderr,
            )
            print(f"Recieved: '{whl_format}'")
            return 1

        flagged = {
            "build": None,
            "python_tags": None,
            "abi_tags": None,
            "platform_tags": None,
        }
        # parse format string
        for k in flagged.keys():
            if _whl_format.group(k) != "*":
                flagged[k] = _whl_format.group(k)

    # search for requested distribution type in pkg.urls
    # and download distribution
    success = False
    bad_key = False
    for url in pkg.urls:
        if url.packagetype == dist_type:
            if dist_type == "bdist_wheel":
                whl_match = WHLRGX.match(url.filename)
                for k, v in flagged.items():
                    if v is not None and v != whl_match.group(k):
                        bad_key = True
                        break
                if bad_key:
                    bad_key = False
                    continue
            if dest is None:
                dest = url.filename
            
            # this can possibly be done in a 'safer' manner with async,
            # but i'm too lazy rn and it doesn't seem like *that* much of
            # a pressing issue
            th = threading.Thread(target=_download, args=(url.url, dest))
            th.start()
            import time
            l = ['/', '|', '\\', '-']
            count = 0
            mb_size = round(url.size/1.049e+6, 1)
            while th.is_alive():
                print(f"[{l[count]}] [{round(msg_board['_download']['bytes_read']/1.049e+6, 1)} / {mb_size} MB] Downloading {pkg.release_name} ({dist_type})...", end = "\r")
                count += 1
                if count == len(l):
                    count = 0
                time.sleep(0.1)
            print("\33[2K", end="\r")
            if msg_board["_download"]["status"] == 0:
                print(f"Downloaded {pkg.release_name} ({dist_type}) to {dest}!")
            else:
                print(msg_board["_download"]["error"])
                return msg_board['_download']['status']
            #s, f = _download(url.url, dest)
            #print("Wrote", s, "bytes to", f)
            success = True
            break
    if not success:
        print(
            f"Unable to find a release of package '{pkg.release_name}' with the given parameters:\n"
            f"\tWheel format: '{whl_format}'\n"
            f"\tPackage type: '{dist_type}'"
        )
    return int(not success)
