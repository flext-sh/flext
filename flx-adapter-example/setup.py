#!/usr/bin/env python3
"""Setup script for the project_name package.

This setup script is provided for backward compatibility with pip.
For normal development and installation, use Poetry.
"""

import os

from setuptools import find_packages, setup

# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Read version from __init__.py
with open(os.path.join("project_name", "__init__.py"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip("\"'")
            break
    else:
        version = "0.1.0"

# Define package metadata
setup(
    name="project_name",
    version=version,
    description="A comprehensive Python client library and CLI tools template for RESTful APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/your-organization/project_name",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "httpx>=0.26.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=0.1.0",
        "rich>=13.5.0",
        "structlog>=24.1.0",
        "click>=8.1.3",
    ],
    entry_points={
        "console_scripts": [
            "cli-tool=project_name.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
