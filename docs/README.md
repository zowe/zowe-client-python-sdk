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
1. Create a virtual environment and install all dependencies:
    - `python -m venv venv`
    - `python -m pip install -r docs/requirements.txt`
2. On the terminal, navigate to the docs folder and run `make html`
    - `cd docs`
    - `make html`
3. On the file explorer, navigate to the `<repo>/docs/build/html/` directory
4. Open the `index.html` in a browser.