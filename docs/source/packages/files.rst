z/OS Files
============

Contains the z/OSMF Files REST API functionalities.

Installing
----------

.. code-block::

   pip install zowe.zos_files_for_zowe_sdk


Reference
---------

.. toctree::
   :maxdepth: 2

   ../classes/zos_files/index

Interacting with USS via z/OSMF
===============================

The Zowe Client Python SDK leverages the z/OS Management Facility (z/OSMF) REST interface to interact with Unix System Services (USS) on z/OS. 
Rather than connecting directly to USS, the Python SDK/the SDK uses z/OSMF as a standardized conduit for file operations and other USS functionalities. 
This design offers several benefits:

- **Standardization:** z/OSMF provides a consistent REST API for interacting with various z/OS components, including USS.
- **Security and maintainability:** By utilizing z/OSMF, Use z/OSMF to benefit from its built-in authentication, logging, and error-handling mechanisms, making integration more robust.
- **Simplified integration:** The REST-based approach reduces the complexity of direct USS interactions, allowing for easier maintenance and future enhancements.

In summary, it might appear that all USS functionality is routed through z/OSMF, this approach is intentional, providing a secure and manageable interface to z/OS USS.

Paramiko and Encoding Considerations
======================================

When using Paramiko to interact with z/OS UNIX System Services (USS), it is important to consider encoding and the handling of special characters. 
By default, Paramiko decodes responses using UTF-8, but z/OS USS may return data in an EBCDIC codepage (e.g., IBM-1047, IBM-037, etc.). 
This mismatch can result in unexpected output, particularly with special characters like ``ööö``, ``👍``, or ``🔟``.

If you experience unexpected characters in your output, please check your terminal's encoding settings (for example, using ``locale`` on Linux). 
Note that certain commands may change the terminal's codepage, which can affect subsequent outputs. 
In such cases, resetting the terminal's encoding after command execution is recommended.
