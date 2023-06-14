import sys
from setuptools import find_namespace_packages, setup
sys.path.append("src")
from _version import __version__

setup(
    name="zowe",
    version=__version__,
    packages=["zowe"],
    package_dir={"zowe": "src"}
)
