import os
import sys
import textwrap
import argparse
from datetime import datetime
from typing import Optional, Tuple
from otlet.api import PackageObject
from otlet.packaging.version import parse, Version
from otlet.markers import DEPENDENCY_ENVIRONMENT_MARKERS
from . import download, config


def print_releases(pkg: PackageObject, args: argparse.Namespace):
    verbose_print(print_releases, "Printing all available releases matching the following criteria:")
    class BottomVersion(Version):
        def __init__(self) -> None:
            super().__init__("0")
        @property
        def epoch(self) -> int:
            return -2

    if args.after_version:
        bottom_version = Version(args.after_version[0])
    else:
        bottom_version = BottomVersion()
    verbose_print(print_releases, f"after version: {bottom_version}")
    top_version = Version(args.before_version[0])
    verbose_print(print_releases, f"before version: {top_version}")
    bottom_date = datetime.fromisoformat(args.after_date[0] + "T23:59:59")
    verbose_print(print_releases, f"after date: {bottom_date}")
    top_date = datetime.fromisoformat(args.before_date[0] + "T00:00:00")
    verbose_print(print_releases, f"before date: {top_date}")

    for rel, obj in pkg.releases.items():
        _rel = parse(rel)
        if top_version <= _rel or bottom_version >= _rel:
            continue
        if top_date < obj.upload_time or bottom_date > obj.upload_time:
            continue

        text = f"({obj.upload_time.date()}) {rel}"
        if obj.yanked:
            text = "\u001b[9m\u001b[1m" + text + "\u001b[0m"
            text += "\u001b[1m\u001b[33m (yanked)\u001b[0m"
        print(text)

    return 0


def print_distributions(
    pkg: PackageObject,
    distributions: Optional[dict] = None,
    dist_type: Optional[str] = None,
    opt_dict: Optional[dict] = None,
):
    if distributions is None:
        verbose_print(print_distributions, "No distribution list supplied. Running download.get_dists()")
        distributions = download.get_dists(pkg, opt_dict)
    if not distributions:
        print(f"No distributions found for {pkg.release_name}", file=sys.stderr)
        return 1

    last_num = 0
    if (distributions) and not dist_type or dist_type == "bdist_wheel":
        print(
            f"Wheels available for {pkg.release_name}:\n"
            "\n[num] [size]\t[build] | [python_tag] | [abi_tag] | [platform_tag]"
        )
        for num, whl in distributions.items():
            if whl["dist_type"] != "bdist_wheel":
                continue
            print(
                f"\u2500\u2500\u2500\u2500\u2500\n{num} "
                f"({whl['converted_size']} {whl['size_measurement']})"
                f"\t{whl['build_tag']} | {whl['python_tag']} | {whl['abi_tag']} | {whl['platform_tag']}"
            )
            last_num += 1
        print()

    if len(distributions) > last_num and dist_type != "bdist_wheel":
        # only do this part if non-wheel distributions are available,
        # or non-wheel dist_type is requested
        print(
            f"'{dist_type if dist_type else 'Other'}' distributions available for {pkg.release_name}:\n"
            "\n[num] [size]\t[distribution_type] | [filename]"
        )
        for num, dist in distributions.items():
            if dist["dist_type"] == "bdist_wheel" or (
                dist_type and dist["dist_type"] != dist_type
            ):
                continue
            print(
                f"\u2500\u2500\u2500\u2500\u2500\n{num} "
                f"({dist['converted_size']} {dist['size_measurement']})"
                f"\t{dist['dist_type']} | {dist['filename']}"
            )

    print()
    return 0


def print_vulns(pkg: PackageObject):
    if pkg.vulnerabilities is None:
        print("\u001b[32mNo vulnerabilities found for this release! :)\u001b[0m")
        return 0

    VULNERABILITY_COUNT = len(pkg.vulnerabilities)
    os.system("clear" if os.name != "nt" else "cls")

    for vuln in pkg.vulnerabilities:
        print(
            "\u001b[1m\u001b[31m==",
            VULNERABILITY_COUNT,
            "security vulnerabilities found for",
            pkg.release_name + "!",
            "==\n\u001b[0m",
        )

        print(pkg.vulnerabilities.index(vuln) + 1, "/", VULNERABILITY_COUNT, sep="")
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


def print_notices(pkg: PackageObject):
    print(f"Notices for package '{pkg.release_name}':\n")
    count = 0
    if pkg.vulnerabilities:
        VCOUNT = len(pkg.vulnerabilities)
        if VCOUNT >= 10:
            color = "\u001b[31m"
        else:
            color = "\u001b[33m"
        print(
            f'\t\u001b[37m- This version has \u001b[1m{color}{VCOUNT}\u001b[0m\u001b[37m known security vulnerabilities.\n\t\t\u001b[37;1m- These can be viewed with the "-r" flag.\u001b[0m'
        )
        count += 1
    if pkg.info.yanked:
        print(
            f"\t\u001b[37m- This version has been yanked from PyPI:\n\t\t\u001b[37;1m- '{pkg.info.yanked_reason}'\u001b[0m"
        )
        count += 1
    if pkg.info.requires_python and not DEPENDENCY_ENVIRONMENT_MARKERS[
        "python_full_version"
    ].fits_constraints(pkg.info.requires_python):
        print(
            f"\t\u001b[37m- '{pkg.release_name}' is incompatible with your current Python version. \n\t\t\u001b[37;1m- (Using '{DEPENDENCY_ENVIRONMENT_MARKERS['python_full_version']}', requires '{pkg.info.requires_python}')\u001b[0m"
        )
        count += 1
    if not count:
        print("\t\u001b[32m- No notices for this release! :)\u001b[0m")
    print()
    return 0


def check_args(args: argparse.Namespace) -> Tuple[PackageObject, int]:
    code = 2
    verbose_print(check_args, "Fetching package data from PyPI/Warehouse")
    if "releases" in sys.argv or args.package_version == "stable":
        pk_object = PackageObject(args.package[0])
    else:
        pk_object = PackageObject(args.package[0], args.package_version)

    if "releases" in sys.argv:
        verbose_print(check_args, "Running print_releases()")
        code = print_releases(pk_object, args)
    elif "download" in sys.argv:
        if args.list_whls:
            verbose_print(check_args, "Running print_distributions()")
            code = print_distributions(
                pk_object, dist_type=args.dist_type, opt_dict=args.whl_options
            )
        else:
            verbose_print(check_args, "Running download.download_dist()")
            code = download.download_dist(
                pk_object, args.dest, args.dist_type, args.whl_options
            )
    elif args.vulnerabilities:
        # List all known vulnerabilities for a release.
        verbose_print(check_args, "Running print_vulns()")
        code = print_vulns(pk_object)
    elif args.urls:
        # List all available URLs for a release.
        verbose_print(check_args, "Printing all available URLs for package")
        if pk_object.info.project_urls is None:
            print(f"No URLs available for {pk_object.release_name}")
        else:
            for _type, url in pk_object.info.project_urls.items():
                print(f"{_type}: {url}")
        code = 0
    elif args.list_extras:
        # List all allowable extras for a release.
        verbose_print(check_args, "Printing all available extras for package")
        print(f"Allowable extras for '{pk_object.release_name}' are:")
        for extra in pk_object.info.possible_extras:
            print(f"\t- {pk_object.canonicalized_name}[{extra}]")
        code = 0
    elif args.notices:
        verbose_print(check_args, "Running print_notices()")
        code = print_notices(pk_object)
    return (pk_object, code)


def verbose_print(calling_function, msg: str) -> None:
    if config["verbose"]:
        print(f"\u001b[38;5;245m[{calling_function.__name__}(): {hex(id(calling_function))}]", msg, "\u001b[0m", file=sys.stderr)


__all__ = ["check_args"]
