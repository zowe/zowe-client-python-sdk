# Contributing

This document contains the contribution guidelines for the Zowe Client Python SDK.

Notice that the Python SDK is still in early development stages, meaning that major architectural changes might be made by the development team at any given moment. **For this reason, only bug fixes and documentation changes are being accepted as contribution at this moment** . This document will be updated as soon as the stable release of the SDK is published (v1.0.0)

- [Contributing](#contributing)
  - [Git branching model](#git-branching-model)
  - [Pull requests](#pull-requests)
  - [Running Tests](#running-tests)
  - [Building Docs](#building-docs)
  - [Code standards](#code-standards)

Git branching model
-------------------

This project follows the [Git flow](https://nvie.com/posts/a-successful-git-branching-model/) branching model.

Pull requests
-------------

Consider the following when you interact with pull requests:

* Pull request reviewers should be assigned to a same-team member.
* Pull requests should remain open for at least 24 hours, or until close of the business next business day (accounting for weekends and holidays).
* Anyone can comment on a pull request to request delay on merging or to get questions answered.

Running Tests
-------------
The project's test suite can be run with the python test runner, `pytest`.  
All test and regular dependencies are included here:
```
pip install -r requirements.txt
```  
Commands for running all unit/integration tests from their respective folder:  
```
pytest tests/unit
```  
```
pytest tests/integration
```  
More information on pytest's usage can be found [here](https://docs.pytest.org/en/7.1.x/how-to/usage.html).

In order to run integration tests, you will need to have a mainframe account and team profile configuration files properly set up.  
Information on creating team profile configuration files can be found [here](https://docs.zowe.org/stable/user-guide/cli-using-using-team-profiles).

You will also need to update the [zowe.config.json](https://docs.zowe.org/stable/user-guide/cli-using-team-configuration-application-developers/#editing-team-profiles) file with the neccessary information.

Building Docs
-------------

The project's documentation is published on [ReadTheDocs.io](https://zowe-client-python-sdk.readthedocs.io/).

To build the docs from source locally, you need these prerequisites:

* [Sphinx](https://www.sphinx-doc.org/en/master/usage/installation.html) - Python Documentation Generator
* Python packages - `pip install -r docs/requirements.txt`

Run `make html` in the docs directory to generate HTML files in "docs/build/html" that can be previewed in your browser.

Docs are generated from reStructuredText (.rst) files in "docs/source" and Python docstrings in the source code which also use reST markup. A quick reference for reStructuredText markup can be found [here](https://docutils.sourceforge.io/docs/user/rst/quickref.html).

Code standards
--------------

This project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
