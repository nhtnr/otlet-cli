import sys
from argparse import ArgumentParser
from .arguments import *

if "releases" in sys.argv:
    RELEASES_ARGUMENT_LIST["package"] = PACKAGE_ARGUMENT
elif "download" in sys.argv:
    DOWNLOAD_ARGUMENTS_LIST["package"] = PACKAGE_ARGUMENT
    DOWNLOAD_ARGUMENTS_LIST["package_version"] = PACKAGE_VERSION_ARGUMENT
else:
    ARGUMENT_LIST["package"] = PACKAGE_ARGUMENT
    ARGUMENT_LIST["package_version"] = PACKAGE_VERSION_ARGUMENT


class OtletArgumentParser(ArgumentParser):
    def __init__(self):
        super().__init__(
            prog="otlet",
            description="Retrieve information about packages available on PyPI",
            epilog="(c) 2022-present Noah Tanner, released under the terms of the MIT License",
        )
        self.arguments = ARGUMENT_LIST
        self.releases_arguments = RELEASES_ARGUMENT_LIST
        self.download_arguments = DOWNLOAD_ARGUMENTS_LIST
        for key, arg in self.arguments.items():
            self.add_argument(
                *arg["opts"], **self.without_keys(arg, ["opts"]), dest=key
            )
        scinit = [
            _ for _ in ["releases", "download", "--help", "-h"] if _ in sys.argv
        ]  # i did this because i can
        if scinit:
            self.subparsers = self.add_subparsers(
                parser_class=ArgumentParser, metavar="[ sub-commands ]"
            )
            self.releases_subparser = self.subparsers.add_parser(
                "releases",
                description="List releases for a specified package",
                help="List releases for a specified package",
                epilog="(c) 2022-present Noah Tanner, released under the terms of the MIT License",
            )
            self.download_subparser = self.subparsers.add_parser(
                "download",
                description="Download package distribution files from PyPI CDN",
                help="Download package distribution files from PyPI CDN",
                epilog="(c) 2022-present Noah Tanner, released under the terms of the MIT License",
            )
            for key, arg in self.releases_arguments.items():
                self.releases_subparser.add_argument(
                    *arg["opts"], **self.without_keys(arg, ["opts"]), dest=key
                )
            for key, arg in self.download_arguments.items():
                self.download_subparser.add_argument(
                    *arg["opts"], **self.without_keys(arg, ["opts"]), dest=key
                )

    def without_keys(self, d, keys):
        return {x: d[x] for x in d if x not in keys}
