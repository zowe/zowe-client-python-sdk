import sys
from setuptools import find_packages, setup
sys.path.append("src")
from _version import __version__

setup(
    name="zowe",
    version=__version__,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
