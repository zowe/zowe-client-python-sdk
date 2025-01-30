# Zowe CLient Python SDK - ReadTheDocs

This document is intended to help you build the documentation that will eventually make its way into the live site: [https://zowe-client-python-sdk.readthedocs.io/en/latest/index.html](https://zowe-client-python-sdk.readthedocs.io/en/latest/index.html)

## Installation requirements

- Python 3.13 or above: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Sphinx: [https://www.sphinx-doc.org/en/master/usage/installation.html#os-specific-package-manager](https://www.sphinx-doc.org/en/master/usage/installation.html#os-specific-package-manager)
  - Windows users may need to install Chocolatey: [https://chocolatey.org/install](https://chocolatey.org/install)
    - I suggest going through the NodeJS installer and opt-in to instal Chocolatey in the final step
    ![node-setup-choco](https://user-images.githubusercontent.com/3109072/68096791-82350c00-fe89-11e9-8cfa-b4619ce96162.jpg)
- Enchant: (Optional) [https://pyenchant.github.io/pyenchant/install.html](https://pyenchant.github.io/pyenchant/install.html)

## Build steps

These steps should help you to build the documentation

0. Clone the repository, open a terminal, and `cd` into the repository directory
1. Install project dependencies:
    - `npm install`
2. Create a virtual environment:
    - `npm run env:create`
3. Activate the virtual environment:
    - `npm run env:activate`
4. Install the doc dependencies
    - `npm run doc:install`
5. Build and open the documentation:
    - `npm run doc:dev`

## Best practices

When using paramiko to interact with z/OS UNIX System Services (USS), it's important to consider encoding and special character handling. 
Since z/OS uses EBCDIC-based encodings (e.g., IBM-1047, IBM-037, etc.), some commands may return unexpected results when processed in a UTF-8 environment. This is because by default, paramiko reads responses in UTF-8, but z/OS USS may return data in an EBCDIC codepage.
Certain special characters, such as ööö, 👍, or 🔟, may not be correctly interpreted if the encoding is mismatched.
If you experience unexpected characters in output, check the terminal's encoding settings (local command on Linux).
Some commands may alter the terminal's codepage, affecting subsequent outputs.
For example, switching between ASCII and EBCDIC on mainframes can impact character interpretation.
If a command affects encoding, reset it after execution.