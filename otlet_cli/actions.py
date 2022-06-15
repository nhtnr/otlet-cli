import sys
from typing import List
from argparse import Action, SUPPRESS
from . import __version__

class OtletVersionAction(Action):

    def __init__(self,
                 option_strings,
                 version=None,
                 dest=SUPPRESS,
                 default=SUPPRESS,
                 help="show program's version number and exit"):
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)
        self.version = __version__

    def __call__(self, parser, namespace, values, option_string=None):
        import os
        import textwrap
        WHITE = (
            "\u001b[38;5;255m"
            if os.environ.get("TERM") == "xterm-256color"
            else "\u001b[37m"
        )
        ART_COLOR = (
            "\u001b[38;5;120m" # light green
            if os.environ.get("TERM") == "xterm-256color"
            else "\u001b[32m"
        )
        parser._print_message(
            textwrap.dedent(
                f"""
                        {ART_COLOR}°º¤ø,¸¸,ø¤º°`°º¤ø,¸,ø¤°º¤ø,¸¸,ø¤º°`°º¤ø,¸

                        {WHITE}otlet v{self.version}
                        {WHITE}(c) 2022-present Noah Tanner, released under the terms of the MIT License

                        {ART_COLOR}°º¤ø,¸¸,ø¤º°`°º¤ø,¸,ø¤°º¤ø,¸¸,ø¤º°`°º¤ø,¸ \u001b[0m\n
                """  # ascii art sourced from http://1lineart.kulaone.com
            ),
            sys.stdout
        )
        parser.exit(0)
