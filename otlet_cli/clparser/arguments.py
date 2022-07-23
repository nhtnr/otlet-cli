from typing import Dict, Any
from .actions import OtletVersionAction

VERBOSE_ARGUMENT: Dict[str, Any] = {
    "opts": ["--verbose"],
    "help": "be verbose",
    "action": "store_true"
}

PACKAGE_ARGUMENT: Dict[str, Any] = {
    "opts": [],
    "metavar": ("package_name"),
    "nargs": 1,
    "type": str,
    "help": "The name of the package to search for",
}

PACKAGE_VERSION_ARGUMENT: Dict[str, Any] = {
    "opts": [],
    "metavar": ("package_version"),
    "default": "stable",
    "nargs": "?",
    "type": str,
    "help": "The version of the package to search for (optional)",
}

ARGUMENT_LIST: Dict[str, Any] = {
    "list_extras": {
        "opts": ["-e", "--list-extras"],
        "help": "list all possible extras for a release.",
        "action": "store_true",
    },
    "notices": {
        "opts": ["-n", "--notices"],
        "help": "list all available notices for a release.",
        "action": "store_true",
    },
    "urls": {
        "opts": ["--urls"],
        "help": "print list of all relevant URLs for package",
        "action": "store_true",
    },
    "vulnerabilities": {
        "opts": ["--vulns", "--vulnerabilities"],
        "help": "print information about known vulnerabilities for package release version",
        "action": "store_true",
    },
    "version": {
        "opts": ["-v", "--version"],
        "help": "print version and exit",
        "action": OtletVersionAction,
    },
}

RELEASES_ARGUMENT_LIST: Dict[str, Any] = {
    # DEFER TO 1.1
    #    "show_vulnerable": {
    #        "opts": ["--show-vulnerable"],
    #        "help": "Not implemented",
    #        "action": "store_true",
    #    },
    "before_date": {
        "opts": ["-bd", "--before-date"],
        "metavar": ("DATE"),
        "help": "Return releases before specified date (YYYY-MM-DD)",
        "nargs": 1,
        "action": "store",
    },
    "after_date": {
        "opts": ["-ad", "--after-date"],
        "metavar": ("DATE"),
        "help": "Return releases after specified date (YYYY-MM-DD)",
        "nargs": 1,
        "action": "store",
    },
    "before_version": {
        "opts": ["-bv", "--before-version"],
        "metavar": ("VERSION"),
        "help": "Return releases before specified version",
        "nargs": 1,
        "action": "store",
    },
    "after_version": {
        "opts": ["-av", "--after-version"],
        "metavar": ("VERSION"),
        "help": "Return releases after specified version",
        "nargs": 1,
        "action": "store",
    },
}

DOWNLOAD_ARGUMENTS_LIST: Dict[str, Any] = {
    "dist_type": {
        "opts": ["-d", "--dist"],
        "metavar": ("DIST_TYPE"),
        "help": "Type of distribution to download (Default: bdist_wheel)",
        "nargs": "?",
        "action": "store",
    },
    "dest": {
        "opts": ["-o", "--output"],
        "metavar": ("FILENAME"),
        "help": "File name to save distribution as (optional)",
        "nargs": "?",
        "action": "store",
    },
    "whl_format": {
        "opts": ["-f", "--whl-format"],
        "metavar": ("FORMAT"),
        "help": "Match format for desired wheel.   ({build_tag}-{python_tag}-{abi_tag}-{platform_tag}, wildcard=*)",
        "nargs": "?",
        "action": "store",
    },
    #"list_dls": {
    #    "opts": ["-l", "--list"],
    #    "help": "TBD",
    #    "action": "store_true",
    #}
}
