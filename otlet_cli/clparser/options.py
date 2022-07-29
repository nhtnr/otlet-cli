import sys
from argparse import ArgumentParser
from .arguments import *

if "releases" in sys.argv:
    RELEASES_ARGUMENT_LIST["package"] = PACKAGE_ARGUMENT
    RELEASES_ARGUMENT_LIST["verbose"] = VERBOSE_ARGUMENT
elif "download" in sys.argv:
    DOWNLOAD_ARGUMENTS_LIST["package"] = PACKAGE_ARGUMENT
    DOWNLOAD_ARGUMENTS_LIST["package_version"] = PACKAGE_VERSION_ARGUMENT
    DOWNLOAD_ARGUMENTS_LIST["verbose"] = VERBOSE_ARGUMENT
else:
    ARGUMENT_LIST["package"] = PACKAGE_ARGUMENT
    ARGUMENT_LIST["package_version"] = PACKAGE_VERSION_ARGUMENT
    ARGUMENT_LIST["verbose"] = VERBOSE_ARGUMENT


class OtletArgumentParser(ArgumentParser):
    def __init__(self):
        super().__init__(
            prog="otlet",
            description="Retrieve information about packages available on PyPI",
            epilog="(c) 2022-present Noah Tanner, released under the terms of the MIT License",
        )
        self.active_parsers = [(ARGUMENT_LIST, self)]
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
                epilog=self.epilog,
            )
            self.download_subparser = self.subparsers.add_parser(
                "download",
                description="Download package distribution files from PyPI CDN",
                help="List releases for a specified package",
                epilog=self.epilog,
            )
            self.active_parsers.append((RELEASES_ARGUMENT_LIST, self.releases_subparser))
            self.active_parsers.append((DOWNLOAD_ARGUMENTS_LIST, self.download_subparser))
        self.init_args(self.active_parsers)

    def init_args(self, parsers):
        for arg_list, parser in parsers:
            for key, arg in arg_list.items():
                parser.add_argument(
                    *arg["opts"], **self.without_keys(arg, ["opts"]), dest=key
                )

    def without_keys(self, d, keys):
        return {x: d[x] for x in d if x not in keys}
