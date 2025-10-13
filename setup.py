#!/usr/bin/env python3
"""
Setup file for Xatra package (for backward compatibility).
Modern installations should use pyproject.toml.
"""

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        packages=find_packages(where="src"),
        package_dir={"": "src"},
    )

