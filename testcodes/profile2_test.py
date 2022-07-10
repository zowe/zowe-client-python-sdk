import sys

sys.path.insert(
    0, '/home/sm/Public/zowe/zowe-client-python-sdk/src/core/zowe/')

from core_for_zowe_sdk import ProfileManager


instance = ProfileManager()
props = instance.load(profile_type="zosmf")
print(props)
print(instance.config_dir)
