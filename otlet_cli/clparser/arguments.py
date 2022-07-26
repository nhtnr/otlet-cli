from typing import Dict, Any
from .actions import OtletVersionAction, OtletWheelDownloadOptsAction

VERBOSE_ARGUMENT: Dict[str, Any] = {
    "opts": ["-v", "--verbose"],
    "help": "be verbose",
    "action": "store_true",
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
        "opts": ["-u", "--urls"],
        "help": "print list of all relevant URLs for package",
        "action": "store_true",
    },
    "vulnerabilities": {
        "opts": ["-r", "--vulnerabilities"],
        "help": "print information about known vulnerabilities for package release version",
        "action": "store_true",
    },
    "version": {
        "opts": ["-V", "--version"],
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
        "default": ["9999-12-31"],
        "nargs": 1,
        "action": "store",
    },
    "after_date": {
        "opts": ["-ad", "--after-date"],
        "metavar": ("DATE"),
        "help": "Return releases after specified date (YYYY-MM-DD)",
        "default": ["1970-01-01"],
        "nargs": 1,
        "action": "store",
    },
    "before_version": {
        "opts": ["-bv", "--before-version"],
        "metavar": ("VERSION"),
        "help": "Return releases before specified version",
        "default": ["100!0"],
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
    "whl_options": {
        "opts": ["-w", "--whl-options"],
        "action": OtletWheelDownloadOptsAction,
    },
    "dest": {
        "opts": ["-o", "--output"],
        "metavar": ("FILENAME"),
        "help": "File name to save distribution as (optional)",
        "nargs": "?",
        "action": "store",
    },
    "list_whls": {
        "opts": ["-l", "--list"],
        "help": "List all available wheels for a project.",
        "action": "store_true",
    },
}
