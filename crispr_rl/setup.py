"""Setup script for crispr_rl package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="crispr_rl",
    version="0.1.0",
    author="CRISPR Design Team",
    author_email="team@example.com",
    description="Reinforcement Learning for CRISPR Guide Design",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/crispr_design_platform",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "numpy>=1.21.0",
    ],
    extras_require={
        "dev": ["pytest>=6.0", "pytest-cov", "flake8", "black", "isort"],
    },
    entry_points={
        "console_scripts": [
            "crispr-design=crispr_rl.cli:main",
        ],
    },
)