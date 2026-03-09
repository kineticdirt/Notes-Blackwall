"""
Setup script for Nightshade Tracker
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="nightshade-tracker",
    version="0.1.0",
    description="Poisoning-Concurrent Watermarking System for Image Protection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nightshade Tracker Team",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "scipy>=1.11.0",
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "imagehash>=4.3.1",
        "reedsolo>=1.7.0",
        "tqdm>=4.66.0",
        "click>=8.1.0",
        "pyyaml>=6.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "nightshade-tracker=cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
