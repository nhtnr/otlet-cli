import os
import sys
import textwrap
import argparse
from typing import Optional
from otlet import api


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

    pkg = api.get_package(package)
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
    pkg = api.get_package(package)
    if pkg.info.project_urls is None:
        print(f"No URLs available for {pkg.release_name}")
        return 0

    for _type, url in pkg.info.project_urls.__dict__.items():
        print(f"{_type}: {url}")

    return 0


def print_vulns(package: str, version: str):
    if version == "stable":
        pkg = api.get_package(package)
    else:
        pkg = api.get_package(package, version)

    if pkg.vulnerabilities is None:
        print("No vulnerabilities found for this release! :)")
        return 0

    os.system("clear" if os.name != "nt" else "cls")
    print(
        "==",
        len(pkg.vulnerabilities),
        "security vulnerabilities found for",
        pkg.release_name,
        "==\n",
    )

    for vuln in pkg.vulnerabilities:
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


def download_dist(
    package_name: str,
    package_version: str,
    dist_type: Optional[str] = None,
    dest: Optional[str] = None,
):
    """Frontend for otlet.api.download_dist()"""
    if package_version == "stable":
        package_version = None # type: ignore
    if dist_type == None:
        dist_type = "bdist_wheel"
    return api.download_dist(package_name, package_version, dist_type, dest) # type: ignore


__all__ = ["print_releases", "print_urls", "print_vulns"]
