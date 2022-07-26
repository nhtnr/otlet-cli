"""
otlet.cli
======================
CLI tool for returning PyPI package information, using the otlet wrapper
"""
#
# Copyright (c) 2022 Noah Tanner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import signal
import textwrap
import urllib
from argparse import Namespace
from typing import Optional, List
import arrow
from otlet import exceptions
from otlet.api import PackageDependencyObject
from otlet.markers import DEPENDENCY_ENVIRONMENT_MARKERS

from . import util, __version__, config
from .clparser.options import OtletArgumentParser


def init_args() -> Optional[Namespace]:
    parser = OtletArgumentParser()

    args = parser.parse_args()
    if not args.package:
        print(
            "Please supply a package to search for: i.e. 'otlet sampleproject'",
            file=sys.stderr,
        )
        return None
    if parser.__dict__.get("subparsers"):
        args.__dict__["subparsers"] = []
        for s in parser.__dict__.get("subparsers").choices:
            args.__dict__["subparsers"].append(s)

    else:
        args.__dict__["subparsers"] = []

    config["verbose"] = args.verbose
    return args


def main():

    signal.signal(
        signal.SIGINT, lambda *_: (_ for _ in ()).throw(SystemExit(0))
    )  # no yucky exception on KeyboardInterrupt (^C)
    args = init_args()
    if not args:
        return 1
    try:
        pkg, check_return = util.check_args(args)
        if check_return != 2:
            return check_return
    except exceptions.PyPIAPIError as err:
        print("otlet: " + str(err), file=sys.stderr)
        return 1

    def generate_release_date(dto) -> str:
        if dto:
            ar_date = arrow.get(dto).to("local")
            return f"{ar_date.humanize()} ({ar_date.strftime('%Y-%m-%d at %H:%M')})"
        return "Unknown"

    def generate_dep_list(deps: List[PackageDependencyObject]) -> str:
        dstr = ""
        if not deps:
            return dstr
        for dep in deps:
            dstr += f"\t\t{dep.name}"
            if dep.version_constraints:
                dstr += f" ({', '.join(dep.version_constraints)})"
            dstr += "\n"
        return dstr

    def get_notice_count():
        count = 0
        if pkg.vulnerabilities:
            count += 1
        if pkg.info.yanked:
            count += 1

        if pkg.info.requires_python and not DEPENDENCY_ENVIRONMENT_MARKERS[
            "python_full_version"
        ].fits_constraints(pkg.info.requires_python):
            count += 1
        if count:
            return f"\n\u001b[33;1;3m**{count}**\u001b[0m\u001b[33m notice(s) for this release.\n    - Use '--notices' for more information\u001b[0m\n"
        return ""

    msg = textwrap.dedent(
        f"""Info for package {pkg.release_name}
{get_notice_count()}
    Summary: {pkg.info.summary}
    Release date: {generate_release_date(pkg.upload_time)}
    Homepage: {pkg.info.home_page}
    PyPI URL: {pkg.info.package_url}
    Documentation: {pkg.info.project_urls.get("Documentation", "N/A") if pkg.info.project_urls else "N/A"}
    Author: {pkg.info.author} <{pkg.info.author_email}>
    Maintainer: {pkg.info.maintainer or pkg.info.author} <{pkg.info.maintainer_email or pkg.info.author_email}>
    License: {pkg.info.license}
    Python Version(s): {pkg.info.requires_python or "Not Specified"}
    Dependencies: {pkg.dependency_count} \n {generate_dep_list(pkg.dependencies)}
    """
    )
    print(msg)
    return 0


def run_cli():
    try:
        code = main()
    except urllib.error.URLError:
        print(
            "Unable to connect to PyPI... Check connection and try again.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    if code != 0:
        util.verbose_print(f"Otlet failed with exit code: {code}")
    raise SystemExit(code)
