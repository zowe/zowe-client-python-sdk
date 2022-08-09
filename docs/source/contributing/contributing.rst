Contributing
==============

This document contains the contribution guidelines for the Zowe Client Python SDK.

Notice that the Python SDK is still in early development stages, meaning that major architectural changes might be made by the development team at any given moment. **For this reason, only bug fixes and documentation changes are being accepted as contribution at this moment** . This document will be updated as soon as the stable release of the SDK is published (v1.0.0)

* :ref:`git-branch`
* :ref:`pull-requests`
* :ref:`running-tests`
* :ref:`building-docs`
* :ref:`code-standards`

.. _git-branch:

Git branching model
-------------------

This project follows the `Git flow`_ branching model.

.. _pull-requests:

Pull requests
-------------

Consider the following when you interact with pull requests:

* Pull request reviewers should be assigned to a same-team member.
* Pull requests should remain open for at least 24 hours, or until close of the business next business day (accounting for weekends and holidays).
* Anyone can comment on a pull request to request delay on merging or to get questions answered.

.. _running-tests:

Running Tests
-------------

The project's test suite can be run with the python test runner, `green`

.. code-block::

  green -vvv  ./tests/unit

In order to run the integration test, one will need to have a zowe profile
and configure the `.env` file: `ZOWE_TEST_PROFILE='<myProfile>'`. If zowe cli is
installed, the test profile lives in `~/.zowe/profiles/zosmf/<myProfile>.yaml`.

.. code-block::

  host: example.com
  port: 443
  user: XXXXX
  password: XXXXX
  rejectUnauthorized: false
  protocol: https

.. _building-docs:

Building Docs
-------------

The project's documentation is published on `ReadTheDocs.io <https://zowe-client-python-sdk.readthedocs.io/>`_.

To build the docs from source locally, you need these prerequisites:

* `Sphinx <https://www.sphinx-doc.org/en/master/usage/installation.html>`_ - Python Documentation Generator
* Python packages - `pip install -r docs/requirements.txt`

Run `make html` in the docs directory to generate HTML files in "docs/build/html" that can be previewed in your browser.

Docs are generated from reStructuredText (.rst) files in "docs/source" and Python docstrings in the source code which also use reST markup. A quick reference for reStructuredText markup can be found `here <https://docutils.sourceforge.io/docs/user/rst/quickref.html>`_.

.. _code-standards:

Code standards
--------------

This project follows the `PEP 8`_ style guide.

.. _PEP 8: https://www.python.org/dev/peps/pep-0008/
.. _Git flow: https://nvie.com/posts/a-successful-git-branching-model/
