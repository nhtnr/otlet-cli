import os
import sys
import textwrap
import argparse
from typing import Optional, Tuple
from otlet.exceptions import *
from otlet.api import PackageObject
from otlet.packaging.version import parse
from . import download


def _print_releases(args: Optional[argparse.Namespace] = None):
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
        _rel = parse(rel)
        if _top_version < _rel or _bottom_version > _rel:
            continue
        if _top_date < obj.upload_time or _bottom_date > obj.upload_time:
            continue

        text = f"({obj.upload_time.date()}) {rel}"
        if obj.yanked:
            text = "\u001b[9m\u001b[1m" + text + "\u001b[0m"
            text += "\u001b[1m\u001b[33m (yanked)\u001b[0m"
        print(text)

    return 0

def _print_vulns(pkg: PackageObject):
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
        msg += f"\n\u001b[1mFixed in version(s):\u001b[0m '{', '.join([str(_) for _ in vuln.fixed_in]).strip(', ')}'\n"
        msg += f"(See more: '{vuln.link}')\n"
        print(msg)
        input("== Press ENTER for next page ==")
        os.system("clear" if os.name != "nt" else "cls")

    return 0

def check_args(args: argparse.Namespace) -> Tuple[PackageObject, int]:
    code = 2
    if args.package_version == "stable":
        pk_object = PackageObject(args.package[0])
    else:
        pk_object = PackageObject(args.package[0], args.package_version)

    if args.subparsers:
        if "releases" in sys.argv:
            code = _print_releases(args)
        if "download" in sys.argv:
            code = download.download_dist(
                pk_object, args.dest, args.whl_format, args.dist_type
            )
    elif args.vulnerabilities:
        """List all known vulnerabilities for a release."""
        code = _print_vulns(pk_object)
    elif args.urls:
        """List all available URLs for a release."""
        if pk_object.info.project_urls is None:
            print(f"No URLs available for {pk_object.release_name}")
        else:
            for _type, url in pk_object.info.project_urls.items():
                print(f"{_type}: {url}")
        code = 0
    elif args.list_extras:
        """List all allowable extras for a release."""
        print(f"Allowable extras for '{pk_object.release_name}' are:")
        for e in pk_object.info.possible_extras:
            print(f"\t- {pk_object.canonicalized_name}[{e}]")
        code = 0
    return (pk_object, code)


__all__ = ["check_args"]
