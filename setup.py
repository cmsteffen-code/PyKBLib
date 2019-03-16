import pathlib
import re
from setuptools import setup
import sys

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
PACKAGE_NAME = "pykblib"

CONST_TEXT = (HERE / f"{PACKAGE_NAME}/const.py").read_text()
VERSION = re.search("__version__ = \"([^']+)\"", CONST_TEXT).group(1)

setup(
    name="PyKBLib",
    version=VERSION,
    description="A Python library for interacting with the Keybase CLI tools.",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords="pykblib keybase library",
    url="https://github.com/cmsteffen-code/PyKBLib",
    project_urls={
        "Source Code": "https://github.com/cmsteffen-code/PyKBLib",
        "Documentation": "https://pykblib.readthedocs.io/en/latest/",
    },
    author="CMSteffen",
    author_email="cmsteffen@protonmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=[PACKAGE_NAME],
    include_package_data=True,
    install_requires=[],
    entry_points={},
)
