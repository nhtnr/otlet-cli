import os
import textwrap
import argparse
from urllib.request import urlopen
from typing import Optional, BinaryIO, Tuple, Union
from io import BufferedWriter
#from otlet import api
from otlet.exceptions import *
from otlet.api import PackageObject


def print_releases(args: Optional[argparse.Namespace] = None):
    from datetime import datetime
    from otlet.packaging.version import etc, Version

    package = args.package[0]  # type: ignore
    _top_version = etc.TopVersion()
    _bottom_version = etc.BottomVersion()
    _top_date = datetime.fromisoformat("9999-12-31T23:59:59")
    _bottom_date = datetime.fromtimestamp(0)

    if args and args.after_version:
        _bottom_version = Version(args.after_version[0])
    if args and args.before_version:
        _top_version = Version(args.before_version[0])
    if args and args.after_date:
        _bottom_date = datetime.fromisoformat(args.after_date[0] + "T23:59:59")
    if args and args.before_date:
        _top_date = datetime.fromisoformat(args.before_date[0] + "T23:59:59")

    pkg = PackageObject(package)
    for rel, obj in pkg.releases.items():
        if _top_version < rel or _bottom_version > rel:
            continue
        if _top_date < obj.upload_time or _bottom_date > obj.upload_time:
            continue

        text = f"({obj.upload_time.date()}) {rel}"
        if obj.yanked:
            text = "\u001b[9m\u001b[1m" + text + "\u001b[0m"
            text += "\u001b[1m\u001b[33m (yanked)\u001b[0m"
        print(text)

    return 0


def print_urls(package: str):
    pkg = PackageObject(package)
    if pkg.info.project_urls is None:
        print(f"No URLs available for {pkg.release_name}")
        return 0

    for _type, url in pkg.info.project_urls.items():
        print(f"{_type}: {url}")

    return 0


def print_vulns(package: str, version: str):
    if version == "stable":
        pkg = PackageObject(package)
    else:
        pkg = PackageObject(package, version)

    if pkg.vulnerabilities is None:
        print("\u001b[32mNo vulnerabilities found for this release! :)\u001b[0m")
        return 0

    os.system("clear" if os.name != "nt" else "cls")

    for vuln in pkg.vulnerabilities:
        print(
            "\u001b[1m\u001b[31m==",
            len(pkg.vulnerabilities),
            "security vulnerabilities found for",
            pkg.release_name + '!',
            "==\n\u001b[0m",
        )

        print(
            pkg.vulnerabilities.index(vuln) + 1, "/", len(pkg.vulnerabilities), sep=""
        )
        msg = ""
        msg += f"\u001b[1m{vuln.id} ({', '.join(vuln.aliases).strip(', ')})\u001b[0m\n"
        msg += textwrap.TextWrapper(initial_indent="\t", subsequent_indent="\t").fill(
            vuln.details
        )
        msg += f"\n\u001b[1mFixed in version(s):\u001b[0m '{', '.join(vuln.fixed_in).strip(', ')}'\n"
        msg += f"(See more: '{vuln.link}')\n"
        print(msg)
        input("== Press ENTER for next page ==")
        os.system("clear" if os.name != "nt" else "cls")

    return 0


def _download(url: str, dest: Union[str, BinaryIO]) -> Tuple[int, Optional[str]]:
    """Download a binary file from a given URL. Do not use this function directly."""
    # download file and store bytes
    request_obj = urlopen(url)
    data = request_obj.read()

    # enforce that we downloaded the correct file, and no corruption took place
    from hashlib import md5

    data_hash = md5(data).hexdigest()
    cloud_hash = request_obj.headers["ETag"].strip('"')
    if data_hash != cloud_hash:
        raise HashDigestMatchError(
            data_hash,
            cloud_hash,
            f'Hashes do not match. (data_hash ("{data_hash}") != cloud_hash ("{cloud_hash}")',
        )

    # write bytes to destination and return
    bw = 0
    if isinstance(dest, str):
        dest = open(dest, "wb")
    with dest as f:
        bw = f.write(data)
    return bw, dest.name


def download_dist(
    package: str,
    release: str,
    dist_type: str = "bdist_wheel",
    dest: Optional[Union[str, BinaryIO]] = None,
) -> bool:
    """
    Download a specified package's distribution file.

    :param package: Name of desired package to download
    :type package: str

    :param release: Version of package to download (Default: stable)
    :type release: Optional[str]

    :param dist_type: Type of distribution to download (Default: bdist_wheel)
    :type dist_type: str

    :param dest: Destination for downloaded output file (Default: current directory with original filename)
    :type dest: Optional[Union[str, BinaryIO]]
    """
    if (
        isinstance(dest, BufferedWriter) and dest.mode != "wb"
    ):  # enforce BufferedWriter is in binary mode
        print("If using BufferedWriter for dest, ensure it is opened in 'wb' mode.")
        return False

    if release == "stable":
        release = None # type: ignore
    if dist_type == None:
        dist_type = "bdist_wheel"

    # search for package on PyPI
    try:
        pkg = PackageObject(package, release)
    except (PyPIPackageNotFound, PyPIPackageVersionNotFound) as e:
        print(e.__str__())
        return False

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
    return success


__all__ = ["print_releases", "print_urls", "print_vulns", "download_dist"]
