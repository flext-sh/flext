#!/usr/bin/env python
"""Django's command-line utility for REDACTED_LDAP_BIND_PASSWORDistrative tasks.

Provides Django management commands for running the web application,
database migrations, static file collection, and REDACTED_LDAP_BIND_PASSWORDistrative tasks.

Examples:
--------
    Basic module usage:

    ```python
    python manage.py runserver
    python manage.py migrate
    ```

Note:
----
    Standard Django management entry point for web application REDACTED_LDAP_BIND_PASSWORDistration.

"""

import os
import sys

from django.core.management import execute_from_command_line


def main() -> None:
    """Run Django REDACTED_LDAP_BIND_PASSWORDistrative tasks.

    Sets up the Django settings module and executes management commands
    from the command line. This is the entry point for all Django
    management operations like runserver, migrate, collectstatic, etc.

    The settings module is set to 'flx_web.flx_web.settings' by default
    but can be overridden with the DJANGO_SETTINGS_MODULE environment variable.

    Raises
    ------
        ImportError: If Django is not installed or not in PYTHONPATH.

    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flx_web.settings")
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
