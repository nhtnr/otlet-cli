import re
import sys
from urllib.request import urlopen
from typing import Tuple, Optional
from otlet import PackageObject
from otlet.exceptions import *

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
        return bw, f.name


def download_dist(
    package: str,
    release: str,
    dest: str,
    format: Optional[str] = None,
    dist_type: Optional[str] = None,
) -> int:
    """
    Download a specified package's distribution file.
    """

    if dist_type != "bdist_wheel" and format:
        print(f"Specified custom .whl format, but requested '{dist_type}'. Ignoring...", file=sys.stderr)

    if release == "stable":
        release = None # type: ignore
    if dist_type is None:
        dist_type = "bdist_wheel"
    if dist_type == "bdist_wheel":
        if format is None:
            format = "*-*-*-*"
        _format = TAGRGX.match(format)
        if _format is None:
            print("Improper format used. Should be '{build_tag}-{python_tag}-{abi_tag}-{platform_tag}'", file=sys.stderr)
            print(f"Recieved: '{format}'")
            return 1

        flagged = {
            "build": None,
            "python_tags": None,
            "abi_tags": None,
            "platform_tags": None
        }
        # parse format string
        for k in flagged.keys():
            if _format.group(k) != '*':
                flagged[k] = _format.group(k)

    # search for package on PyPI
    try:
        pkg = PackageObject(package, release)
    except (PyPIPackageNotFound, PyPIPackageVersionNotFound) as e:
        print(e.__str__())
        return 1

    # search for requested distribution type in pkg.urls
    # and download distribution
    success = False
    bad_key = False
    for url in pkg.urls:
        if url.packagetype == dist_type:
            if dist_type == "bdist_wheel":
                whl_match = WHLRGX.match(url.filename)
                for k in flagged.keys():
                    if flagged[k] is not None and flagged[k] != whl_match.group(k):
                        bad_key = True
                        break
                if bad_key:
                    bad_key = False
                    continue
            if dest is None:
                dest = url.filename
            s, f = _download(url.url, dest)
            print("Wrote", s, "bytes to", f)
            success = True
            break
    if not success:
        print(
            f'Unable to find a release of package \'{pkg.release_name}\' with the given parameters:\n'
            f'\tWheel format: \'{format}\'\n'
            f'\tPackage type: \'{dist_type}\''
        )
    return int(not success)