import os
import textwrap
import argparse
from typing import Optional
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


__all__ = ["print_releases", "print_urls", "print_vulns"]
