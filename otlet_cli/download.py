import re
import sys
from urllib.request import urlopen
from typing import Tuple, Optional
from otlet import PackageObject
from otlet.exceptions import *

# This regex pattern was taken from version 1.4.1 of the 'wheel_filename' package
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

def _download(url: str, dest: str) -> Tuple[int, Optional[str]]:
    """Download a binary file from a given URL. Do not use this function directly."""
    # download file and store bytes
    request_obj = urlopen(url)
    data = request_obj.read()

    # enforce that we downloaded the correct file, and no corruption took place
    from hashlib import md5

    data_hash = md5(data).hexdigest()
    cloud_hash = request_obj.headers["ETag"].strip('"')
    if data_hash != cloud_hash:
        print("File hash doesn't match, and the file may have been corrupted. Please try again...", file=sys.stderr)
        raise SystemExit(1)

    # write bytes to destination and return
    bw = 0
    with open(dest, "wb") as f:
        bw = f.write(data)
    return bw, dest.name


def download_dist(
    package: str,
    release: str,
    dist_type: str = "bdist_wheel",
    dest: Optional[str] = None,
) -> int:
    """
    Download a specified package's distribution file.
    """

    if release == "stable":
        release = None # type: ignore
    if dist_type == None:
        dist_type = "bdist_wheel"

    # search for package on PyPI
    try:
        pkg = PackageObject(package, release)
    except (PyPIPackageNotFound, PyPIPackageVersionNotFound) as e:
        print(e.__str__())
        return 1

    # search for requested distribution type in pkg.urls
    # and download distribution
    success = False
    for url in pkg.urls:
        if url.packagetype == dist_type:
            if dest is None:
                dest = url.filename
            s, f = _download(url.url, dest)
            print("Wrote", s, "bytes to", f)
            success = True
            break
    if not success:
        print(
            f'Distribution type "{dist_type}" not available for this version of "{package}".'
        )
    return int(not success)