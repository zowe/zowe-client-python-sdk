import glob
import os.path
import sys
from setuptools import setup
sys.path.append("src")
from _version import __version__

sdk_dirs = [path for path in glob.iglob("src/*") if os.path.isdir(path)]
packages = ["zowe"]
package_dirs = {"zowe": "src"}
for sdk_dir in sorted(sdk_dirs):
    if not os.path.isfile(os.path.join(sdk_dir, "setup.py")):
        continue
    sdk_name = os.path.basename(sdk_dir)
    pkg_name = f"zowe.{sdk_name}_for_zowe_sdk"
    packages.append(pkg_name)
    package_dirs[pkg_name] = os.path.join(sdk_dir, "zowe", f"{sdk_name}_for_zowe_sdk")
setup(
    name="zowe",
    version=__version__,
    packages=packages,
    package_dir=package_dirs
)
