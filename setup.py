#!/usr/bin/env python3
"""
Setup script for VidyaMitra Career Agent
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="vidyamitra-career-agent",
    version="1.0.0",
    author="Shaan Yadav",
    author_email="shaanyadav1012004@gmail.com",
    description="VidyaMitra - AI-Powered Resume Evaluator, Trainer & Career Planner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shaanyadav/vidyamitra-career-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "flake8>=6.0",
            "pytest-cov>=4.0",
        ],
        "test": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vidyamitra=backend.app.main:app",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)