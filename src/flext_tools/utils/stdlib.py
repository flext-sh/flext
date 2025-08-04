"""FLEXT Tools Python Standard Library Utilities - Module Identification.

This utility module provides functions to identify Python standard library modules
for dependency analysis in the FLEXT ecosystem. Used by workspace tools to
distinguish between stdlib and third-party dependencies.

Key Components:
    - get_stdlib_modules: Returns comprehensive set of Python stdlib modules
    - Module categorization for better dependency analysis

Integration:
    - Core utility used by FLEXT workspace dependency discovery
    - Enables accurate separation of stdlib vs external dependencies

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

Author: FLEXT Development Team
Version: 2.0.0
License: MIT
"""

from __future__ import annotations

import sys


def get_stdlib_modules() -> set[str]:
    """Return comprehensive set of Python standard library modules.

    Returns:
        Set containing names of all Python standard library modules

    """
    try:
        # Use builtin_module_names from current system (safer than subprocess)
        builtin_modules = set(sys.builtin_module_names)

        # Add known stdlib modules not included in builtin_module_names
        stdlib_extras = {
            # Collections and data structures
            "collections",
            "functools",
            "itertools",
            "operator",
            # Types and abstractions
            "typing",
            "dataclasses",
            "enum",
            "abc",
            "types",
            # I/O and file system
            "pathlib",
            "io",
            "os",
            "sys",
            "shutil",
            "tempfile",
            # Date and time
            "datetime",
            "time",
            "calendar",
            "zoneinfo",
            # Data formats
            "json",
            "csv",
            "configparser",
            "tomllib",
            "xml",
            "html",
            # Mathematics and numbers
            "math",
            "decimal",
            "fractions",
            "statistics",
            "random",
            # Text and string processing
            "string",
            "re",
            "textwrap",
            "difflib",
            "unicodedata",
            # System and processes
            "subprocess",
            "threading",
            "multiprocessing",
            "asyncio",
            "concurrent",
            # Network and communication
            "socket",
            "http",
            "urllib",
            "email",
            "ipaddress",
            # Security and cryptography
            "hashlib",
            "secrets",
            "uuid",
            "hmac",
            # General utilities
            "logging",
            "warnings",
            "traceback",
            "inspect",
            "copy",
            "copyreg",
            "contextlib",
            "atexit",
            "weakref",
            "gc",
            "getpass",
            "fnmatch",
            # Development and testing
            "unittest",
            "doctest",
            "pdb",
            "profile",
            "timeit",
            # Outros
            "pickle",
            "shelve",
            "sqlite3",
            "zlib",
            "gzip",
            "bz2",
            "lzma",
            "base64",
            "binascii",
            "struct",
            "codecs",
            "locale",
            "gettext",
            "argparse",
            "getopt",
            "readline",
            "rlcompleter",
            "platform",
            "errno",
            "ctypes",
            "array",
            "queue",
            "heapq",
            "bisect",
            "pprint",
            "reprlib",
            "dis",
            "ast",
            "tokenize",
            "keyword",
            "builtins",
            "__future__",
            "imp",
            "importlib",
            "pkgutil",
            "modulefinder",
            "runpy",
            "site",
            "sysconfig",
            "venv",
            "numbers",
            "cmath",
            "audioop",
            "chunk",
            "colorsys",
            "imghdr",
            "ossaudiodev",
            "sndhdr",
            "wave",
            "cgi",
            "cgitb",
            "wsgiref",
            "ftplib",
            "poplib",
            "imaplib",
            "smtplib",
            "telnetlib",
            "socketserver",
            "xmlrpc",
            "ssl",
            "select",
            "selectors",
            "signal",
            "mmap",
            "msvcrt",
            "winreg",
            "winsound",
            "posix",
            "pwd",
            "grp",
            "termios",
            "tty",
            "pty",
            "fcntl",
            "resource",
            "syslog",
            "pipes",
            "pathlib2",
            "contextvars",
        }

        return builtin_modules | stdlib_extras

    except (AttributeError, ImportError):
        # Fallback para lista mínima se algo falhar
        return {
            "os",
            "sys",
            "re",
            "json",
            "math",
            "random",
            "datetime",
            "time",
            "pathlib",
            "typing",
            "collections",
            "itertools",
            "functools",
            "subprocess",
            "threading",
            "asyncio",
            "unittest",
            "logging",
            "copy",
            "operator",
            "contextlib",
            "io",
            "string",
            "types",
        }
