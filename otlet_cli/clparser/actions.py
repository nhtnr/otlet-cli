import sys
from argparse import Action, SUPPRESS
from .. import __version__
from otlet import __version__ as api_version


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
