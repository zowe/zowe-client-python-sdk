z/OS UNIX System Services (USS) Package
=======================================

Provides APIs to interact with z/OS UNIX System Services (USS) over SSH (using z/OSMF or other SSH connections).

Examples
--------

### Issuing a command in the z/OS USS environment

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_uss_for_zowe_sdk import Uss

profile = ProfileManager().load(profile_name="ssh")

with Uss(profile) as uss:
    uss.connect()

    print(uss.execute_command(command="ls -la", cwd="/u/home"))
    
    uss.disconnect()
```

### Possible Limitations

Some commands executed via SSH may change the code page (character encoding) of the remote session, leading to unexpected behavior.
This is especially relevant for z/OS USS environments, where different data sets or terminal settings may use EBCDIC (e.g., IBM-1047) instead of UTF-8.
If you encounter encoding issues, ensure that your session consistently uses UTF-8 or explicitly specify the correct encoding when reading output.

Also, the Paramiko SSH library may not always handle special characters correctly (e.g., ööö, 👍, 🔟) due to encoding mismatches. 
This can happen if:
- The remote shell is using a different encoding than expected.
- The Python script does not explicitly decode the output.
If you run into issues, try explicitly decoding `stdout`/`stderr` using the correct encoding.
Lastly, to avoid encoding problems when retrieving command output, explicitly decode the response using UTF-8 (or the appropriate encoding for your environment). 
Meanwhile, if dealing with EBCDIC-based systems (e.g., z/OS), you may need to decode using IBM-specific encodings

## Best practices

When using paramiko to interact with z/OS UNIX System Services (USS), it is important to consider encoding and special character handling. 
Since z/OS uses EBCDIC-based encodings (e.g., IBM-1047, IBM-037, etc.), some commands may return unexpected results when processed in a UTF-8 environment. This is because by default, paramiko reads responses in UTF-8, but z/OS USS may return data in an EBCDIC codepage.
Certain special characters, such as ööö, 👍, or 🔟, may not be correctly interpreted if the encoding is mismatched.
If you experience unexpected characters in output, check the terminal's encoding settings (local command on Linux).
Some commands may alter the terminal's codepage, affecting subsequent outputs.
For example, switching between ASCII and EBCDIC on mainframes can impact character interpretation.
If a command affects encoding, reset it after execution.