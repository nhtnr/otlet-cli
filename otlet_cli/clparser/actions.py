import re
import sys
from argparse import Action, SUPPRESS
from .. import __version__
from otlet import __version__ as api_version


class OtletWheelDownloadOptsAction(Action):
    def __init__(
        self,
        option_strings,
        dest=SUPPRESS,
        default=None,
        help="supply options for which wheels to show, i.e. 'python_tag:cp39' to only show wheels with the 'cp39' attribute for 'python_tag'",
    ):
        super().__init__(
            option_strings=option_strings,
            metavar=("WHL_OPTS"),
            dest=dest,
            default=default,
            nargs="?",
            help=help,
        )

    def __call__(self, parser, namespace, values, option_string):
        # create dictionary for user-desired options pattern matching
        acceptable_options = ["build_tag", "python_tag", "abi_tag", "platform_tag"]
        STAR = "(?:.*)"
        opt_dict = {}
        for i in values.split(","):
            opt_match = re.match(r"(?:\s)?(\S+):(\S+)", i)
            opt_value = re.compile(opt_match.group(2).replace("*", STAR))
            if opt_match.group(1) not in acceptable_options:
                print(f"error: unrecognized option '{opt_match.group(1)}'. ignoring...")
                continue
            opt_dict[opt_match.group(1)] = opt_value
        setattr(namespace, "whl_options", opt_dict)


class OtletVersionAction(Action):
    def __init__(
        self,
        option_strings,
        dest=SUPPRESS,
        default=SUPPRESS,
        help="show program's version number and exit",
    ):
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
        )
        self.version = __version__

    def __call__(self, parser, *args, **kwargs):
        import os
        import textwrap

        WHITE = (
            "\u001b[38;5;255m"
            if os.environ.get("TERM") == "xterm-256color"
            else "\u001b[37m"
        )
        ART_COLOR = (
            "\u001b[38;5;120m"  # light green
            if os.environ.get("TERM") == "xterm-256color"
            else "\u001b[32m"
        )
        parser._print_message(
            textwrap.dedent(
                f"""
                        {ART_COLOR}°º¤ø,¸¸,ø¤º°`°º¤ø,¸,ø¤°º¤ø,¸¸,ø¤º°`°º¤ø,¸

                        {WHITE}otlet-cli v{self.version}
                        {WHITE}otlet v{api_version}
                        {WHITE}(c) 2022-present Noah Tanner, released under the terms of the MIT License

                        {ART_COLOR}°º¤ø,¸¸,ø¤º°`°º¤ø,¸,ø¤°º¤ø,¸¸,ø¤º°`°º¤ø,¸ \u001b[0m\n
                """  # ascii art sourced from http://1lineart.kulaone.com
            ),
            sys.stdout,
        )
        parser.exit(0)
