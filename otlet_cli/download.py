import re
import os
import sys
from hashlib import md5
from urllib.request import urlopen
from typing import Optional
from otlet import PackageObject
import threading
from . import util

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
msg_board = {"_download": {"bytes_read": 0}}


def get_dists(pkg: PackageObject, opt_dict: Optional[dict] = None) -> dict:
    distributions = {}
    for num, url in enumerate(pkg.urls):
        _match = WHLRGX.match(url.filename)
        if not _match:
            distributions[num + 1] = {
                "filename": url.filename,
                "download_url": url.url,
                "dist_type": url.packagetype,
                "converted_size": round(url.size / 1.049e6, 1)
                if url.size > 1048576
                else round(url.size / 1024, 1),
                "size_measurement": "MiB" if url.size > 1048576 else "KiB",
            }
            continue
        distributions[num + 1] = {
            "filename": url.filename,
            "download_url": url.url,
            "dist_type": "bdist_wheel",
            "build": _match.group("build"),
            "python_tags": _match.group("python_tags"),
            "abi_tags": _match.group("abi_tags"),
            "platform_tags": _match.group("platform_tags"),
            "converted_size": round(url.size / 1.049e6, 1)
            if url.size > 1048576
            else round(url.size / 1024, 1),
            "size_measurement": "MiB" if url.size > 1048576 else "KiB",
        }

    if not opt_dict:
        return distributions

    for key, dist in distributions.copy().items():
        if dist["dist_type"] != "bdist_wheel":  # ignore non-wheels for obvious reasons
            continue
        for opt, pattern in opt_dict.items():
            if (
                not dist[opt]
                or dist[opt].lower() == "none"
                or dist[opt].lower() == "any"
            ):
                continue
            is_match = pattern.match(dist[opt])
            if not is_match:
                distributions.pop(key)
                break

    return distributions


def _download(url: str, dest: str) -> None:
    """Download a binary file from a given URL. Do not use this function directly."""
    # download file and store bytes
    msg_board["_download"]["status"] = 2
    request_obj = urlopen(url)
    f = open(dest + ".part", "wb")
    while True:
        j = request_obj.read(1024 * 3)  # read one 3K chunk at a time
        if j == b"":
            break
        f.write(j)
        msg_board["_download"]["bytes_read"] += 1024 * 3
    f.close()

    # enforce that we downloaded the correct file, and no corruption took place
    with open(dest + ".part", "rb") as f:
        data_hash = md5(f.read()).hexdigest()
    cloud_hash = request_obj.headers["ETag"].strip('"')
    if data_hash != cloud_hash:
        msg_board["_download"][
            "error"
        ] = "The file was corrupted during download. Please try again..."
        msg_board["_download"]["status"] = 1
        return

    os.rename(dest + ".part", dest)  # remove temp tag
    msg_board["_download"]["status"] = 0


def download_dist(
    pkg: PackageObject, dest: str, dist_type: str, opt_dict: Optional[dict] = None
) -> int:
    """
    Download a specified package's distribution file.
    """

    # get distributions and ask for user selection
    dists = get_dists(pkg, opt_dict)
    dist_types = [x for x in dists.items() if x[1]["dist_type"] == dist_type]
    dist_type_count = len(dist_types)
    if any((not dist_type, dist_type_count > 1)) and len(dists) > 1:
        util._print_distributions(pkg, dists, dist_type)
        while True:
            try:
                dl_number = int(input("Specify a number to download: "))
                break
            except ValueError:
                print("ERROR: Value must be an integer...", file=sys.stderr)
    elif (
        dist_type
    ):  # fall here if dist_type is given, and only one distribution for dist_type exists, i.e. 'sdist'
        try:
            dl_number = dist_types[0][0]
        except IndexError:
            print(
                f"No distributions of type '{dist_type}' found for {pkg.release_name}",
                file=sys.stderr,
            )
            raise SystemExit(1)
    elif not len(dists):
        # rare, but might as well cover it
        print(f"No distributions found for {pkg.release_name}", file=sys.stderr)
        return -1
    else:  # if only one distribution is available, no need to manually select it
        dl_number = 1

    # search for requested distribution type in pkg.urls
    # and download distribution
    if dest is None:
        dest = dists[dl_number]["filename"]

    ### Download distribution from PyPI CDN
    th = threading.Thread(
        target=_download, args=(dists[dl_number]["download_url"], dest)
    )
    th.start()
    import time

    l = ["/", "|", "\\", "-"]
    count = 0
    while th.is_alive():
        size_read = (
            round(msg_board["_download"]["bytes_read"] / 1.049e6, 1)
            if dists[dl_number]["size_measurement"] == "MiB"
            else round(msg_board["_download"]["bytes_read"] / 1024, 1)
        )
        print(
            f"[{l[count]}] [{size_read} / {dists[dl_number]['converted_size']} {dists[dl_number]['size_measurement']}] Downloading {pkg.release_name} ({dists[dl_number]['dist_type']})...",
            end="\r",
        )
        count += 1
        if count == len(l):
            count = 0
        time.sleep(0.1)
    print("\33[2K", end="\r")
    if msg_board["_download"]["status"] == 0:
        print(
            f"Downloaded {pkg.release_name} ({dists[dl_number]['dist_type']}) to {dest}!"
        )
    else:
        print(msg_board["_download"]["error"])
        return msg_board["_download"]["status"]
    return 0
