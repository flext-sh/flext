#!/usr/bin/env python3
"""Setup script for Meltano Bridge for Go integration."""

from setuptools import setup

setup(
    name="meltano-bridge",
    version="0.1.0",
    description="Meltano Bridge for Go Integration using gopy",
    author="FLEXT Team",
    author_email="team@flext.dev",
    py_modules=["meltano_bridge"],
    python_requires=">=3.8",
    install_requires=[
        "meltano>=3.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
