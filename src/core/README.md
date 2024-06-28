Core Package
============

The Zowe Client Python SDK Core package contains functionality that is shared across all other SDK packages, such as `zowe.zos-files-for-zowe-sdk`.  

<strong>Important!</strong> You must install the Core package to satisfy the peer dependency requirement for all other SDK packages.


Core Libraries
------------

Examples of modules, included in this package, and description of the functionality that they provide:

- <em>session</em> - Defines the `Session` class, which sets connection details received from a ProfileManager 
or by passing an `ISession` object with session parameters.
  

- <em>sdk_api</em> - Defines the `SdkApi` class, representing the base SDK API.
  

- <em>profile_manager</em> - Defines the `ProfileManager` class. It contains methods such as `autodiscover_config_dir`,
which autodiscovers Zowe z/OSMF Team Profile Config files; `load`, which loads z/OSMF connection details from a z/OSMF profile and
`load_credentials`, which returns credentials stored for the given config.
