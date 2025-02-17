from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="isolator",
    version="0.1.0",
    description="A secure application isolation tool using bubblewrap",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gemechis Chala Degefa",
    author_email="gemechischala@gmail.com",
    url="https://github.com/scorpidev/isolator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses system bubblewrap
    ],
    entry_points={
        "console_scripts": [
            "isolator=isolator.__main__:main",
        ],
    },
    keywords=["isolation", "sandbox", "security", "container", "bubblewrap"],
    project_urls={
        "Bug Tracker": "https://github.com/scorpidev/isolator/issues",
        "Documentation": "https://github.com/scorpidev/isolator#readme",
        "Source Code": "https://github.com/scorpidev/isolator",
    },
)