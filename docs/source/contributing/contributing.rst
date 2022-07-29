Contributing
==============

This document contains the contribution guidelines for the Zowe Client Python SDK.

Notice that the Python SDK is still in early development stages, meaning that major architectural changes might be made by the development team at any given moment. **For this reason, only bug fixes and documentation changes are being accepted as contribution at this moment** . This document will be updated as soon as the stable release of the SDK is published (v1.0.0)

* :ref:`git-branch`
* :ref:`pull-requests`
* :ref:`running-tests`
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

.. _code-standards:

Code standards
--------------

This project follows the `PEP 8`_ style guide.

.. _PEP 8: https://www.python.org/dev/peps/pep-0008/
.. _Git flow: https://nvie.com/posts/a-successful-git-branching-model/