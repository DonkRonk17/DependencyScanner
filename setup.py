#!/usr/bin/env python3
"""
Setup configuration for DependencyScanner.

Author: ATLAS (Team Brain)
For: Logan Smith / Metaphy LLC
License: MIT
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding='utf-8')

setup(
    name="dependencyscanner",
    version="1.0.0",
    description="Scan Team Brain tools for Python dependency conflicts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ATLAS (Team Brain)",
    author_email="team-brain@metaphy.com",
    url="https://github.com/DonkRonk17/DependencyScanner",
    license="MIT",
    py_modules=["dependencyscanner"],
    python_requires=">=3.8",
    install_requires=[
        # Zero dependencies - stdlib only!
    ],
    extras_require={
        "security": ["safety>=2.0.0"],
        "dev": ["pytest>=7.0"],
    },
    entry_points={
        "console_scripts": [
            "dependencyscanner=dependencyscanner:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Systems Administration",
    ],
    keywords="dependencies analysis conflicts team-brain tools",
)
